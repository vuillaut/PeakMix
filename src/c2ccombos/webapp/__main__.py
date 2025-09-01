from __future__ import annotations

import argparse
import os
from . import create_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="c2ccombos-web", description="Start the c2ccombos Web UI (Flask)")
    parser.add_argument("--host", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, help="Port to bind (default: 8000)")
    args = parser.parse_args()

    app = create_app()
    host = args.host or os.environ.get("HOST", "127.0.0.1")
    port = args.port or int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
