# Focus — Jewellery Store Clone

Three independently-deployed pieces, one repo:

| Folder | What it is | Tech |
|---|---|---|
| `backend/` | REST API | Python / FastAPI / SQLAlchemy |
| `storefront/` | Customer-facing site | Static HTML/CSS/JS |
| `admin/` | Admin console (separate URL) | Static HTML/CSS/JS |

## 1. Local test (optional, in Termux)

```bash
cd backend
pip install -r requirements.txt --break-system-packages
python seed.py          # creates admin user + sample products
uvicorn main:app --reload
```
Then open `storefront/index.html` and `admin/index.html` directly in a browser
(API_BASE_URL in each `js/config.js` already points to `http://localhost:8000/api`).

## 2. Deploy to Render (via GitHub, auto-deploy)

Render reads `render.yaml` at the repo root and creates **three separate
services with three separate URLs** automatically:

- `focus-backend` — the API
- `focus-storefront` — customer site
- `focus-admin` — admin console

### Steps
1. Push this repo to GitHub (commands below).
2. In Render: **New → Blueprint**, connect the GitHub repo, click **Apply**.
3. Render provisions the free Postgres DB + all 3 services and wires
   `DATABASE_URL` automatically.
4. It'll ask you to set `SEED_ADMIN_PASSWORD` (marked `sync: false`) — set it
   to whatever you want your admin login password to be.
5. Once the backend service is live, open its **Shell** tab in Render and run:
   ```bash
   python seed.py
   ```
   This creates the admin login and sample jewelry products.
6. Copy the live backend URL Render gives you (e.g.
   `https://focus-backend.onrender.com`) and update:
   - `storefront/js/config.js` → `API_BASE_URL`
   - `admin/js/config.js` → `API_BASE_URL`

   Commit and push — both static sites auto-redeploy.
7. Log into the admin console with `SEED_ADMIN_EMAIL` /
   `SEED_ADMIN_PASSWORD`.

Every future `git push` to the connected branch auto-redeploys all three
services — that's what "auto-deploy" on Render means; no extra command needed
after the initial GitHub push.
