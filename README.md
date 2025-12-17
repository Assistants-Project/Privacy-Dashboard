# Privacy Dashboard

## Run Environment

### Prerequisites
- Docker and Docker Compose
- Python 3.11 or newer (with `pip`)

### 1. Configure environment variables
Create a `.env` file in the repository root. Adjust the credentials and ports if needed.

```ini
#PROTECTIONS
#SET ALL OF THIS TO TRUE IN PRODUCTION
JWT_COOKIE_SECURE=False #Flask over plain HTTP in development
JWT_COOKIE_CSRF_PROTECT=False

#FLASK
FLASK_ENV=development

#POSTGRES
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DB=privacy_db
POSTGRES_PORT=5434
DEV_DATABASE_URI=postgresql+psycopg2://<user>:<password>@localhost:5434/privacy_db

#SMARTOTUM
SMARTOTUM_BASE_URL=https://api.smartotum.com
SMARTOTUM_DHT_URL=http://house_name.pods.smartotum.com/.dht/
SMARTOTUM_API_BASE_PATH=/auth
SMARTOTUM_RID=emailpassword
SMARTOTUM_AUTH_MODE=header
SMARTOTUM_JWKS_URL=https://api.smartotum.com/auth/jwt/jwks.json
SMARTOTUM_ISSUER=https://api.smartotum.com/auth
SMARTOTUM_RULE_TOPIC=privacy_rule
#supported smartotum devices for rules mapping
SMARTOTUM_DEVICE_TOPICS=domo_light,domo_light_dimmable,domo_rgbw_light,domo_switch,domo_roller_shutter,domo_camera
SMARTOTUM_TIMEOUT=1 #starting timeout in seconds when communicating with Smartotum
```

### 2. Start PostgreSQL via Docker
```bash
docker compose up -d --build
#stop when finished (it will delete the container,network,volume)
docker compose down -v 
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
