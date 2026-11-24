# Payment Gateway (Learn Python)

A local study copy of [Bitcart](https://bitcart.ai), a self-hosted crypto payment gateway. The three apps that make up a running gateway live in this one repository so the Python API can be read next to the two web apps that call it.

The code is Bitcart’s, under the MIT license (copyright MrNaif2018). Each app keeps the license and docs it shipped with. Upstream docs: [docs.bitcart.ai](https://docs.bitcart.ai).

## Layout

```
api/      Merchants API. Python 3.12, FastAPI, PostgreSQL, Redis.
admin/    Merchant panel. Nuxt 2. Stores, wallets, invoices, products.
store/    Customer storefront. Nuxt 2. Catalog, cart, checkout.
```

`api/api/` is the Python package. Imports stay `from api...` because that package name is what the rest of the code expects. `api/main.py` is the process you start.

| Path | What it is | Default URL |
| --- | --- | --- |
| `api/` | Merchants API (`api/main.py`) | http://localhost:8000 |
| `admin/` | Merchant panel | http://localhost:3000 |
| `store/` | Public shop | http://localhost:4000 |

Admin and store both call the API. Admin’s default store link is `localhost:4000`, so the store app is started on port 4000.

```
admin  ──┐
         ├──►  api  ──►  PostgreSQL
store  ──┘       ├──►  Redis
                 ├──►  coin daemon (BTC, LTC, …)
                 └──►  template renderer (Rust)
```

## How a payment moves

1. A merchant creates a store and a wallet in **admin**.
2. A customer opens **store**, adds a product, and checks out.
3. The store asks **api** to create an invoice.
4. The API asks the coin daemon for an address and watches the chain.
5. When the payment confirms, the API marks the invoice paid. It can then email the merchant or send a notification.

Invoice HTML is rendered by the Rust service in `api/renderer/`, not by Python string formatting. Background jobs (notifications, payouts) run in `api/worker.py`, separate from the HTTP process.

## Where to read first

| Question | Start here |
| --- | --- |
| What the API project is | [api/README.md](api/README.md) |
| How to run and test the API | [api/CONTRIBUTING.md](api/CONTRIBUTING.md) |
| Python style used in the API | [api/CODING_STANDARDS.md](api/CODING_STANDARDS.md) |
| Settings and `.env` | [api/conf/README.md](api/conf/README.md), [api/conf/.env.sample](api/conf/.env.sample) |
| Coin daemons | [api/daemons/README.md](api/daemons/README.md) |
| Database changes | [api/migrations/README.md](api/migrations/README.md) |
| Merchant panel | [admin/README.md](admin/README.md), [admin/CONTRIBUTING.md](admin/CONTRIBUTING.md) |
| Storefront | [store/README.md](store/README.md), [store/CONTRIBUTING.md](store/CONTRIBUTING.md) |

Inside `admin/` and `store/`, the `components`, `pages`, `store`, `plugins`, `layouts`, and `middleware` folders each have a short README. Those are Nuxt conventions from the upstream projects.

## Full local run (Windows)

Everything below stays on your machine: PostgreSQL, Redis on `localhost:6379`, and the API on `localhost:8000`. Without Redis, the API can print “ready” but Swagger and App pages hang in the browser.

### 1. PostgreSQL

Create a database (name must match `DB_DATABASE` in `api/conf/.env`, often `bitcart` or `bitcartdb`). Keep Postgres running on port `5432`.

Browse it with pgAdmin, DBeaver, or `psql` — not MySQL Workbench.

### 2. Redis (local, no Docker required)

`uvicorn` only starts the Python API. Redis is a separate server (same idea as PostgreSQL), so that one command cannot also start Redis by itself.

Install Redis once on Windows:

```bat
winget install Redis.Redis
```

Restart the terminal after install so `redis-server` is on PATH. Docker Redis still works if you prefer it, but it is optional.

### 3. API

Install `uv` once if needed:

```bat
py -m pip install uv
```

Then:

```bat
cd api
uv sync --no-dev --group web
copy conf\.env.dev.sample conf\.env
```

Put your Postgres password in `api/conf/.env`:

```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_DATABASE=bitcartdb
```

Use the same database name you created in pgAdmin.

Migrate once, then use the one local command (starts Redis if needed, then the API):

```bat
uv run alembic upgrade head
run_local.bat
```

Or:

```bat
uv run python scripts\run_local.py
```

That is the Windows equivalent of “one command”. Plain `uv run uvicorn ...` still works if Redis is already running.

On Windows, `just` needs a Unix `sh` shell, so use `alembic` / `run_local` as above. Leave this terminal open. The startup banner must show Redis `[UP]`.

| URL | What it is |
| --- | --- |
| http://127.0.0.1:8000 | API docs |
| http://127.0.0.1:8000/swagger | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |
| http://127.0.0.1:8000/openapi.json | OpenAPI schema |

`uv sync --no-dev --group web` installs the API only. A full `uv sync` also builds every coin daemon and can fail on Windows path length limits.

### 4. Admin panel (optional)

New terminal:

```bat
cd admin
yarn
yarn dev
```

http://localhost:3000 → local API at http://localhost:8000

### 5. Storefront (optional)

New terminal:

```bat
cd store
yarn
yarn dev --port 4000
```

http://localhost:4000

### Optional API extras

From `api/`, each in its own terminal (Git Bash or WSL if `just` is used):

```bat
uv run python worker.py
```

Coin daemons and the Rust template renderer are only needed for real on-chain payments and HTML templates.

## Upstream

These folders track three Bitcart repositories. Docker packaging lives in a fourth repo and is not copied here.

- API: https://github.com/bitcart/bitcart
- Admin: https://github.com/bitcart/bitcart-admin
- Store: https://github.com/bitcart/bitcart-store
- Deploy: https://github.com/bitcart/bitcart-docker

## License

MIT. See [api/LICENSE](api/LICENSE), [admin/LICENSE](admin/LICENSE), and [store/LICENSE](store/LICENSE).
