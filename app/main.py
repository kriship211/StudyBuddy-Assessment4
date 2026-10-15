from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.models import AgentRequest, AgentResponse
from app.orchestrator import Orchestrator
from app.tools import TASKS

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
app = FastAPI(title='StudyBuddy Collaborative Task Agents', version='4.0.0',
              description='Assessment 4: Planner and Worker with visible message routing.')
engine = Orchestrator()
app.mount('/static', StaticFiles(directory=ROOT / 'app/static'), name='static')

@app.get('/', include_in_schema=False)
def home():
    return FileResponse(ROOT / 'app/static/index.html')

@app.get('/health')
def health():
    return {'status': 'ok', 'version': '4.0.0', 'agents': ['planner', 'worker']}

@app.get('/api/tasks')
def tasks():
    return TASKS

@app.get('/api/agent/state')
def state():
    return engine.snapshot()

@app.post('/api/agent', response_model=AgentResponse)
async def agent(request: AgentRequest):
    return await engine.run(request)
