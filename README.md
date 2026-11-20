# commerce-api

Maison Douce operational database: schema, opening seed and the operations simulator.

- `db/`: schema `bakery` (34 tables, row audit triggers) and the opening seed. The branch opens on the day the
  database is initialized.
- `simulate_operations.py`: one tick of shop activity (sales, production, purchasing, stock, shifts) covering the
  time since the previous run. Demand follows Open-Meteo weather and the Vietnamese calendar.
- `run.py`: creates the schema on an empty database, then runs a tick every minute.

## Run

The database and its owner role must exist. Connection settings come from `DATABASE_URL` or the standard `PG*`
variables.

```bash
docker build -t commerce-api .
docker run --rm -e PGHOST=... -e PGDATABASE=bakery -e PGUSER=commerce -e PGPASSWORD=... commerce-api
```

Options: `--orders-per-hour` (weekday baseline, default 10), `--interval` (seconds, default 60), `--branch`.
