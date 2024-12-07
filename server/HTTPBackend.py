import json
import os
from typing import Any
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from .Database import Database

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args: Any, database: Database, **kwargs: Any):
        self.__database = database
        super().__init__(*args, **kwargs)

    def __serve_file(self, code: int, mime_type: str, relative_path: str) -> None:
        self.send_response(code)
        self.send_header('Content-Type', f'{mime_type}; charset=utf-8')
        self.end_headers()

        try:
            script_path = os.path.realpath(__file__)
            www_path = os.path.join(os.path.dirname(script_path), 'www')
            absolute_path = os.path.join(www_path, relative_path)

            with open(absolute_path, 'rb') as f:
                self.wfile.write(f.read())
        except OSError:
            pass

    def __serve_agents(self) -> None:
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        json_bytes = json.dumps(self.__database.get_agent_names()).encode('utf-8')
        self.wfile.write(json_bytes)

    def __serve_tasks(self, query: dict[str, list[str]]) -> None:
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        limit_offset = None
        if 'limit' in query and 'offset' in query:
            try:
                limit_offset = int(query['limit'][0]), int(query['offset'][0])
            except ValueError:
                pass

        alerts_only = False
        if 'alerts_only' in query and query['alerts_only'][0].lower() in ['1', 'true']:
            alerts_only = True

        agent_target = None
        if 'agent' in query and 'target' in query:
            agent_target = query['agent'][0], query['target'][0]

        query_result = self.__database.get_tasks(alerts_only, agent_target, limit_offset)
        json_bytes = json.dumps(query_result).encode('utf-8')
        self.wfile.write(json_bytes)

    # pylint: disable-next=invalid-name
    def do_GET(self) -> None:
        url = urlparse(self.path)
        match url.path:
            case '/':
                self.__serve_file(200, 'text/html', 'index.html')
            case '/index.html':
                self.__serve_file(200, 'text/html', 'index.html')
            case '/index.js':
                self.__serve_file(200, 'text/javascript', 'index.js')
            case '/index.css':
                self.__serve_file(200, 'text/css', 'index.css')
            case '/agents':
                self.__serve_agents()
            case '/tasks':
                self.__serve_tasks(parse_qs(url.query, keep_blank_values=True))
            case '/Pele.webp':
                self.__serve_file(200, 'image/webp', 'public/Pele-Routers.webp')
            case _:
                self.__serve_file(404, 'text/html', '404.html')

class HTTPBackend:
    def __init__(self, database: Database, port: int = 8000):
        self.database = database
        self.port = port

    def serve(self) -> None:
        database = self.database

        class DatabaseHandler(HTTPRequestHandler):
            def __init__(self, *args: Any, **kwargs: Any):
                super().__init__(*args, database=database, **kwargs)

        httpd = HTTPServer(('0.0.0.0', self.port), DatabaseHandler)
        httpd.serve_forever()
