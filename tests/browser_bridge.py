"""Serve the real WSGI app over JSON-lines for socket-free browser tests.

Playwright intercepts HTTP requests and forwards them here, preserving the real
application handlers and SQLite operations. This is a test transport, not a
production server or evidence of public deployment.
"""

import base64
from io import BytesIO
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from addressbook.app import Application

application = Application(sys.argv[1])

for line in sys.stdin:
    try:
        request = json.loads(line)
        body = base64.b64decode(request.get("body", ""))
        environ = {
            "REQUEST_METHOD": request["method"],
            "PATH_INFO": request["path"],
            "QUERY_STRING": request.get("query", ""),
            "CONTENT_LENGTH": str(len(body)),
            "CONTENT_TYPE": request.get("headers", {}).get("content-type", ""),
            "HTTP_HOST": "addressbook.test",
            "wsgi.input": BytesIO(body),
        }
        for key, value in request.get("headers", {}).items():
            if key not in ("content-type", "content-length", "host"):
                environ["HTTP_" + key.upper().replace("-", "_")] = value
        response = {}
        def start(status, headers):
            response["status"] = int(status.split()[0])
            response["headers"] = dict(headers)
        data = b"".join(application(environ, start))
        response["body"] = base64.b64encode(data).decode()
        print(json.dumps(response), flush=True)
    except Exception as error:
        print(json.dumps({"bridge_error": str(error)}), flush=True)
