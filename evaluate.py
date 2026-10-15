"""Generate real local-mode execution evidence; never claims live Gemini success."""
import asyncio
import json
from pathlib import Path
from app.models import AgentRequest
from app.orchestrator import Orchestrator

async def main():
    root=Path(__file__).resolve().parent/'evidence'
    root.mkdir(exist_ok=True)
    engine=Orchestrator(root/'generated_logs')
    cases=[('summary','Summarise all tasks','normal'),
           ('lookup','When is task 1 due?','normal'),
           ('priority','Classify report due in 2 days, blocking other work','normal'),
           ('timeout','Summarise tasks','timeout'),
           ('invalid_output','Summarise tasks','invalid_output'),
           ('invalid_receiver','Summarise tasks','invalid_receiver'),
           ('iteration_limit','Summarise tasks','loop')]
    results=[]
    for name,message,scenario in cases:
        result=await engine.run(AgentRequest(message=message,scenario=scenario,timeout_seconds=0.1))
        data=result.model_dump(mode='json')
        (root/f'{name}.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        results.append({'case':name,'status':result.status,'steps':result.steps,'run_id':str(result.run_id)})
    (root/'evaluation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))

if __name__=='__main__':asyncio.run(main())
