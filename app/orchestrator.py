"""Bounded pipeline with validated routing and per-run JSONL evidence."""
import asyncio
import json
import logging
import os
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4
from app.agents import PlannerAgent, WorkerAgent
from app.models import AgentRequest, AgentResponse, Message, Plan, Result

class Orchestrator:
    def __init__(self, log_dir=None):
        self.planner = PlannerAgent()
        self.worker = WorkerAgent()
        self.log_dir = Path(log_dir or os.getenv('STUDYBUDDY_LOG_DIR', Path(__file__).resolve().parents[1] / 'logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.run_count = 0
        self.error_count = 0
        self.history = deque(maxlen=100)

    def snapshot(self):
        with self.lock:
            return {'run_count': self.run_count, 'error_count': self.error_count,
                    'history': list(self.history)}

    async def run(self, request: AgentRequest) -> AgentResponse:
        run_id = uuid4()
        events = []
        steps = 0
        def log(event, **detail):
            entry = {'timestamp': datetime.now(timezone.utc).isoformat(), 'run_id': str(run_id),
                     'event': event, **detail}
            events.append(entry)
            with self.lock:
                with (self.log_dir / 'messages.jsonl').open('a', encoding='utf-8') as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            logging.getLogger('studybuddy').info('%s', json.dumps(entry, ensure_ascii=False))

        def route(sender, receiver, intent, content):
            nonlocal steps
            if steps >= request.max_steps:
                raise RuntimeError('max_iterations')
            message = Message(run_id=run_id, step=steps + 1, sender=sender,
                              receiver=receiver, intent=intent, content=content)
            log('SENT', message=message.model_dump(mode='json'))
            routes = {('orchestrator', 'planner', 'plan'), ('planner', 'worker', 'execute'),
                      ('worker', 'orchestrator', 'result')}
            if (sender, receiver, intent) not in routes:
                raise ValueError('invalid_receiver_or_route')
            if intent == 'execute':
                Plan.model_validate(content)
            elif intent == 'result':
                Result.model_validate(content)
            else:
                if set(content) != {'message'} or not isinstance(content['message'], str):
                    raise ValueError('invalid_plan_input')
            steps += 1
            log('RECEIVED', message=message.model_dump(mode='json'))
            return message

        log('RUN_START', mode=request.mode, scenario=request.scenario, max_steps=request.max_steps)
        status = 'completed'
        try:
            incoming = route('orchestrator', 'planner', 'plan', {'message': request.message})
            plan = Plan.model_validate(await asyncio.wait_for(
                self.planner.receive(incoming.content, request.mode), request.timeout_seconds))
            while True:
                receiver = 'unknown' if request.scenario == 'invalid_receiver' else 'worker'
                handoff = route('planner', receiver, 'execute', plan.model_dump())
                raw = await asyncio.wait_for(self.worker.receive(handoff.content, request.scenario),
                                             request.timeout_seconds)
                result = Result.model_validate(raw)
                # Schema alone cannot guarantee that a worker used the assigned tool.
                expected_tool = plan.action if plan.action != 'general' else None
                if result.action != plan.action or result.used_tool != expected_tool:
                    raise ValueError('result_plan_mismatch')
                route('worker', 'orchestrator', 'result', result.model_dump())
                if request.scenario != 'loop':
                    break
        except Exception as exc:
            status = 'fallback'
            kind = 'timeout' if isinstance(exc, TimeoutError) else type(exc).__name__
            # Avoid external exception strings, which can expose provider response data.
            log('ERROR', error_type=kind, reason='Agent execution or routing failed; inspect scenario and step.')
            result = Result(answer='The request could not be completed safely. No task data was changed. Check the trace and try a normal request.', action='fallback')
            log('FALLBACK', result=result.model_dump())
        with self.lock:
            self.run_count += 1
            self.error_count += int(status == 'fallback')
            self.history.append({'run_id': str(run_id), 'status': status, 'steps': steps})
        log('RUN_END', status=status, steps=steps)
        return AgentResponse(run_id=run_id, status=status, mode=request.mode,
                             result=result, steps=steps, events=events)
