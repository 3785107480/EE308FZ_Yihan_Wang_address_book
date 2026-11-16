#!/usr/bin/env python3
"""Local development entry point. Use Gunicorn for public hosting."""

import argparse
import threading
import webbrowser
from wsgiref.simple_server import make_server

from addressbook.app import Application


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yihan Wang Address Book")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--database", default=None)
    parser.add_argument("--open-browser", action="store_true", help="Open the local app after binding the server")
    args = parser.parse_args()
    application = Application(args.database)
    with make_server(args.host, args.port, application) as server:
        browser_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
        url = f"http://{browser_host}:{args.port}"
        print(f"Address Book is available at {url}", flush=True)
        if args.open_browser:
            opener = threading.Timer(0.5, webbrowser.open, args=(url,))
            opener.daemon = True
            opener.start()
        server.serve_forever()
