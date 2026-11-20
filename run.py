#!/usr/bin/env python3
"""Create the bakery schema on an empty database, then run one simulator tick every minute."""

from __future__ import annotations

import argparse
import os
import signal
import sys
import time
from pathlib import Path

import simulate_operations as simulator

DB_DIR = Path(__file__).with_name("db")
# 33 audited tables plus simulation_runs.
EXPECTED_TABLES = 34

stopping = False


def request_stop(signum, frame):
    global stopping
    stopping = True


def initialize_schema(dsn: str) -> None:
    conn = simulator.db_connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) AS tables FROM information_schema.tables "
                "WHERE table_schema = 'bakery' AND table_type = 'BASE TABLE'"
            )
            tables = cur.fetchone()["tables"]
            if tables == EXPECTED_TABLES:
                print(f"Schema bakery already has {tables} tables, skipping initialization.", flush=True)
                return
            if tables:
                # Replaying the opening seed onto existing data would duplicate it.
                raise RuntimeError(f"Schema bakery has {tables} of {EXPECTED_TABLES} tables; fix it by hand.")
            for path in sorted(DB_DIR.glob("*.sql")):
                cur.execute(path.read_text(encoding="utf-8"))
        conn.commit()
        print(f"Initialized schema bakery from {DB_DIR.name}/.", flush=True)
    finally:
        conn.close()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", default="MAIN", help="Branch code (default: MAIN).")
    parser.add_argument("--orders-per-hour", type=float, default=10, help="Weekday baseline (default: 10).")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between runs (default: 60).")
    parser.add_argument("--once", action="store_true", help="Run one tick and exit with its result.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    # An empty DSN makes libpq read PGHOST, PGUSER, PGPASSWORD and the other PG* variables.
    dsn = os.environ.get("DATABASE_URL", "")
    initialize_schema(dsn)

    run_args = argparse.Namespace(
        dsn=dsn or None, branch=args.branch, orders_per_hour=args.orders_per_hour, seed=None
    )
    if args.once:
        return simulator.simulate(run_args)
    while not stopping:
        started = time.monotonic()
        try:
            simulator.simulate(run_args)
        except Exception as error:
            # A failed run is recorded in simulation_runs; keep going with the next one.
            print(f"Run failed: {error}", file=sys.stderr, flush=True)
        sys.stdout.flush()
        while not stopping and time.monotonic() - started < args.interval:
            time.sleep(1)
    print("Stopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
