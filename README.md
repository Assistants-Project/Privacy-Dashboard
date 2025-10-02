# Privacy Dashboard

## Run Environment

### Prerequisites
- Docker and Docker Compose
- Python 3.11 or newer (with `pip`)

### 1. Configure environment variables
Create a `.env` file in the repository root. Adjust the credentials and ports if needed.

```ini
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DB=privacy_db
POSTGRES_PORT=5434
FLASK_ENV=development
DEV_DATABASE_URI=postgresql+psycopg2://<user>:<password>@localhost:5434/privacy_db
SMARTOTUM_BASE_URL=https://api.smartotum.com
SMARTOTUM_API_BASE_PATH=/auth
SMARTOTUM_RID=emailpassword
SMARTOTUM_AUTH_MODE=header
SMARTOTUM_JWKS_URL=https://api.smartotum.com/auth/jwt/jwks.json
SMARTOTUM_ISSUER=https://api.smartotum.com/auth
SMARTOTUM_TIMEOUT=10
# Set to False if you run Flask over plain HTTP in development
JWT_COOKIE_SECURE=False
```

### 2. Start PostgreSQL via Docker
```bash
docker compose up -d postgres
```

### 3. Create and activate the virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```
(Use `Scripts\\activate` on Windows.)

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply database migrations (first run only)
```bash
cd backend
export FLASK_APP=run.py
flask db upgrade
```

### 6. Run the API server
```bash
export FLASK_APP=run.py   # run this in every new shell session
flask run --debug --port 5000
```
The service is now reachable at `http://localhost:5000`.

## Endpoints

- **Swagger UI / OpenAPI docs:** `http://localhost:5000/docs/swagger`
- **Login:** `POST /api/auth/login` (sets `st_access_token` / `st_refresh_token` cookies)
- **Smartotum homes:** `GET /api/homes` (requires the access-token cookie; maps data from Smartotum’s `/service/systems` endpoint)