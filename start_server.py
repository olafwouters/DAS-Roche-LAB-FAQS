from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser

root = Path(__file__).resolve().parent
server = ThreadingHTTPServer(("127.0.0.1", 8000), partial(SimpleHTTPRequestHandler, directory=str(root)))
threading.Timer(0.7, lambda: webbrowser.open("http://localhost:8000")).start()
print("DAS / Roche Lab FAQS — Original pages: http://localhost:8000 — Ctrl+C to stop.")
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()
