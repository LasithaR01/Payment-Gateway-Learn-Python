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

## Run it locally

You need Git, [uv](https://docs.astral.sh/uv) (Python 3.12+), Node.js with Yarn, PostgreSQL, and Redis. Rust is required only for the template renderer. A coin daemon is required only when you want a real on-chain payment.

Full task list for the API: `cd api` then `just`.

### API

```bash
cd api
uv sync
```

Copy a sample config and edit the database password:

```bash
# Windows PowerShell
Copy-Item conf\.env.dev.sample conf\.env

# macOS / Linux
cp conf/.env.dev.sample conf/.env
```

The API reads `conf/.env`. That file is gitignored. `conf/.env.sample` and `conf/.env.dev.sample` stay in git. Defaults if you skip a value: Postgres database `bitcart` on `127.0.0.1:5432`, user `postgres`, Redis on `127.0.0.1:6379`.

Create the schema, then start the HTTP API:

```bash
just db-migrate
just dev-api
```

That serves http://localhost:8000 with reload. OpenAPI is on that same host.

Two more processes, each in its own terminal, from `api/`:

```bash
just worker      # notifications, payouts, background jobs
just renderer    # Rust template renderer (needs Rust)
```

A Bitcoin daemon, testnet:

```bash
just testnet
```

### Admin

```bash
cd admin
yarn
yarn dev
```

http://localhost:3000. It uses http://localhost:8000 unless you set `BITCART_ADMIN_API_URL`.

To click around without a local API:

```bash
# PowerShell
$env:BITCART_ADMIN_API_URL = "https://api.bitcart.ai"
yarn dev
```

### Store

```bash
cd store
yarn
yarn dev --port 4000
```

http://localhost:4000. API URL override: `BITCART_STORE_API_URL`.

## Upstream

These folders track three Bitcart repositories. Docker packaging lives in a fourth repo and is not copied here.

- API: https://github.com/bitcart/bitcart
- Admin: https://github.com/bitcart/bitcart-admin
- Store: https://github.com/bitcart/bitcart-store
- Deploy: https://github.com/bitcart/bitcart-docker

## License

MIT. See [api/LICENSE](api/LICENSE), [admin/LICENSE](admin/LICENSE), and [store/LICENSE](store/LICENSE).
