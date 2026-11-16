#!/usr/bin/env python3
"""Local development entry point. Use Gunicorn for public hosting."""

import argparse
from wsgiref.simple_server import make_server

from addressbook.app import Application


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yihan Wang Address Book")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--database", default=None)
    args = parser.parse_args()
    application = Application(args.database)
    with make_server(args.host, args.port, application) as server:
        print(f"Address Book is available at http://{args.host}:{args.port}", flush=True)
        server.serve_forever()
