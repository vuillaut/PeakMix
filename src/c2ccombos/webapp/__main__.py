from __future__ import annotations

import os
from . import create_app


def main() -> None:
    app = create_app()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
