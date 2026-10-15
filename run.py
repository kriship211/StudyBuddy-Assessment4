"""Start from any folder: python path/to/run.py; use --no-browser for tests."""
import argparse
import importlib.util
import sys
import threading
import webbrowser
from pathlib import Path

def main():
    missing = [name for name in ('fastapi', 'uvicorn', 'pydantic', 'dotenv', 'httpx')
               if importlib.util.find_spec(name) is None]
    if missing:
        print('Install dependencies first: python -m pip install -r requirements.txt')
        print('Missing packages:', ', '.join(missing))
        return 1
    import uvicorn
    parser = argparse.ArgumentParser(description='Run StudyBuddy locally')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Choose a port between 1024 and 65535')
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    url = f'http://127.0.0.1:{args.port}'
    print(f'Website: {url}\nAPI documentation: {url}/docs')
    if not args.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run('app.main:app', host='127.0.0.1', port=args.port, log_level='info')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
