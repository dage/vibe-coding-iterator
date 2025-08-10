from __future__ import annotations
import uvicorn
from ..adapters.http.api import app


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()


