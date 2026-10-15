import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app import main
from app.agents import PlannerAgent
from app.models import AgentRequest, Message, Plan
from app.orchestrator import Orchestrator

@pytest.fixture
def engine(tmp_path):
    return Orchestrator(tmp_path)

@pytest.fixture
def client(engine, monkeypatch):
    monkeypatch.setattr(main, 'engine', engine)
    return TestClient(main.app)

@pytest.mark.parametrize('message,action,text', [
    ('Summarise all tasks','summarise_tasks','3 tasks'),
    ('When is task 1 due?','lookup_task','2026-09-25'),
    ('Classify report due in 2 days, blocking other work','classify_priority','High'),
    ('Look up task 999','lookup_task','not found'),
    ('What is the weather?','general','I can'),
    ('Classify report due in 10 days, not blocking','classify_priority','Low'),
    ('Classify report due in -2 days','general','non-negative'),
    ('Classify report priority','general','non-negative'),
])
def test_behaviour(client,message,action,text):
    r=client.post('/api/agent',json={'message':message})
    assert r.status_code==200
    body=r.json()
    assert body['status']=='completed'
    assert body['result']['action']==action
    assert text in body['result']['answer']
    assert body['steps']==3

@pytest.mark.parametrize('scenario',['timeout','invalid_output','invalid_receiver','loop'])
def test_failures(client,scenario):
    body=client.post('/api/agent',json={'message':'Summarise tasks','scenario':scenario,'timeout_seconds':0.05}).json()
    assert body['status']=='fallback'
    assert body['steps']<=4
    assert body['result']['action']=='fallback'
    assert any(e['event']=='ERROR' for e in body['events'])
    assert client.get('/health').status_code==200

@pytest.mark.parametrize('payload',[{'message':'a'},{'message':'   '},{'message':'hello','extra':1}, {'message':'hello','max_steps':0},{'message':'hello','timeout_seconds':0}])
def test_invalid_requests(client,payload):
    assert client.post('/api/agent',json=payload).status_code==422
    assert client.get('/api/agent/state').json()['run_count']==0

def test_iteration_limit(client):
    body=client.post('/api/agent',json={'message':'Summarise tasks','max_steps':1}).json()
    assert body['status']=='fallback' and body['steps']==1

def test_trace_and_file(client,engine):
    b=client.post('/api/agent',json={'message':'Summarise tasks'}).json()
    sent=[e['message'] for e in b['events'] if e['event']=='SENT']
    received=[e['message'] for e in b['events'] if e['event']=='RECEIVED']
    assert sent==received
    assert [(m['sender'],m['receiver']) for m in sent]==[('orchestrator','planner'),('planner','worker'),('worker','orchestrator')]
    lines=[json.loads(l) for l in (engine.log_dir/'messages.jsonl').read_text().splitlines()]
    assert lines==b['events']
    assert len({x['run_id'] for x in lines})==1

def test_concurrent_state(engine):
    async def run_all():
        return await asyncio.gather(*(engine.run(AgentRequest(message='Summarise tasks')) for _ in range(10)))
    runs=asyncio.run(run_all())
    assert len({r.run_id for r in runs})==10
    assert engine.snapshot()['run_count']==10

def test_result_mismatch(engine,monkeypatch):
    async def bad(*args):
        return {'answer':'Wrong tool','action':'lookup_task','used_tool':'lookup_task'}
    monkeypatch.setattr(engine.worker,'receive',bad)
    assert asyncio.run(engine.run(AgentRequest(message='Summarise tasks'))).status=='fallback'

def test_bad_plan():
    with pytest.raises(ValidationError):Plan(action='lookup_task')
    with pytest.raises(ValidationError):Plan(action='classify_priority',due_in_days=-1)

def test_gemini_unconfigured(client,monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    b=client.post('/api/agent',json={'message':'Summarise tasks','mode':'gemini'}).json()
    assert b['status']=='fallback' and b['mode']=='gemini'

def test_mocked_gemini(engine,monkeypatch):
    async def fake(text):return Plan(action='summarise_tasks')
    monkeypatch.setattr(engine.planner,'remote_plan',fake)
    b=asyncio.run(engine.run(AgentRequest(message='Give me an overview',mode='gemini')))
    assert b.status=='completed'

def test_website_docs(client):
    for path in ['/','/static/app.js','/static/style.css','/docs','/openapi.json','/api/tasks']:
        assert client.get(path).status_code==200
