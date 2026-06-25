from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config


def run_migrations() -> None:
    """Run Alembic migrations to the latest revision before app startup."""
    project_root = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    command.upgrade(alembic_cfg, "head")


def main() -> None:
    run_migrations()
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
