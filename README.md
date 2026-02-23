# Privacy Dashboard

## Docker

This repository provides:

- `docker-compose.yml`: PostgreSQL only, used only when developing so Database,Backend and Frontend can be launched separately
- `docker-compose-demo.yml`: full stack solution for demo, it includes: frontend + backend + PostgreSQL, when using this flask is in demo mode

### Prerequisites

- Docker and Docker Compose
- Python 3.11 or newer (with `pip`)

### Configure environment variables

- Create a `.env` file in the repository root
- Accurately set the env according to your needs (development|testing|demo)

```ini
#FLASK
FLASK_ENV=development #development|testing|demo
LOGGING_LEVEL=INFO

#SECURITY (change these in real deployments)
SECRET_KEY=<random_secret>
JWT_SECRET_KEY=<random_jwt_secret>

#JWT COOKIES
#Set these to True only when serving over HTTPS (Secure cookies are not sent over plain HTTP)
JWT_COOKIE_SECURE=False
JWT_COOKIE_CSRF_PROTECT=False


#POSTGRES (dev: DB exposed on localhost:${POSTGRES_PORT})
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DB=privacy_db
POSTGRES_PORT=5434
#1 of this at a time is used based on the FLASK_ENV
DEV_DATABASE_URI=postgresql+psycopg2://<user>:<password>@localhost:5434/privacy_db #when development or testing
DEMO_DATABASE_URI=postgresql+psycopg2://<user>:<password>@postgres:5432/privacy_db #when demo

#SMARTOTUM
SMARTOTUM_BASE_URL=https://api.smartotum.com
SMARTOTUM_DHT_URL=https://house_name.pods.smartotum.com/.dht/
SMARTOTUM_API_BASE_PATH=/auth
SMARTOTUM_RID=emailpassword
SMARTOTUM_AUTH_MODE=header
SMARTOTUM_JWKS_URL=https://api.smartotum.com/auth/jwt/jwks.json
SMARTOTUM_ISSUER=https://api.smartotum.com/auth
SMARTOTUM_RULE_TOPIC=privacy_rule #for smartotum rules topic
#supported smartotum devices for rules mapping
SMARTOTUM_DEVICE_TOPICS=domo_light,domo_light_dimmable,domo_rgbw_light,domo_switch,domo_roller_shutter,domo_camera
#starting timeout in seconds when communicating with Smartotum
SMARTOTUM_TIMEOUT=5
#If set, Smartotum applications are loaded from this local JSON file instead of calling the remote API
SMARTOTUM_APPLICATIONS_JSON=./config/smartotum-apps.json
#Token for marketplace ingestion endpoint
MARKETPLACE_INGEST_TOKEN=<set_a_strong_random_token>

#ONTOLOGY
ONTOLOGY_DIRECTORY=app/ontologies/
ONTOLOGY_SIFIS_FILE=sifis-home.owl

#TEMPLATES/SCHEMAS
PRIVACY_NOTICE_TEMPLATE_PATH=./config/privacy-notice-template.json
PIA_TEMPLATE_PATH=./config/privacy-impact-assessment-template.json
PIA_SCHEMA_PATH=./config/privacy-impact-assessment-schema.json

#FRONTEND

#VITE
VITE_API_BASE_URL=http://localhost:5050/api/ #choose same port as the one in flask run --port -> not needed in demo mode
#VITE_API_BASE_URL=/api/ #optional override when frontend is built for demo mode

#CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173 #works for both development and demo mode (because in demo mode frontend and backend are served from the same origin ), chose the same port where the vite frontend is running
```

### Generate required secrets

The minimum secrets required for full app functionality are:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `MARKETPLACE_INGEST_TOKEN`: required only if you use Marketplace ingestion endpoint

You can generate all of them at once with:

```bash
python - <<'PY'
import secrets
print("SECRET_KEY=" + secrets.token_hex(32))
print("JWT_SECRET_KEY=" + secrets.token_hex(32))
print("MARKETPLACE_INGEST_TOKEN=" + secrets.token_urlsafe(24))
PY
```

Then copy the generated values into your `.env`.

Alternative (OpenSSL):

```bash
openssl rand -hex 32      # SECRET_KEY / JWT_SECRET_KEY
openssl rand -base64 24   # MARKETPLACE_INGEST_TOKEN
```

### RUN IN DEVELOPMENT

- When running in development mode is useful to run DB,Backed and frontend separately
- Follow this steps to deploy the application with all the components separately

#### 1. Start PostgreSQL via Docker

```bash
docker compose up -d postgres
# stop when finished (it will delete the container,network,volume)
docker compose down -v
```

#### 2. Create and activate the virtual environment

```bash
python -m venv .venv #or python3 if you use that
source .venv/bin/activate
```

(Use `Scripts\\activate` on Windows.)

#### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### 4. Apply database migrations (first run only)

```bash
cd backend
export FLASK_APP=run.py
flask db upgrade
```

#### 5. Run the backend server

- When running in development the db is populated with initial_data

```bash
export FLASK_APP=run.py   # run this in every new shell session
flask run --debug --port 5050 #use 5050 to avoid airplay port collision on mac os
```

- The backend is now reachable at `http://localhost:5050`.

#### 6. Install frontend dependencies

```bash
cd frontend
npm ci
```

### 7. Run Frontend VITE in development

```bash
npm run dev
```

- The frontend is now reachable by the specified port

### RUN IN TESTING (Smartotum Mock)

- Testing mode uses local mock files under `backend/testing/data` for Smartotum systems, DHT topics and rules.
- This is useful to run backend/API tests without depending on Smartotum availability.
- Make sure to set FLASK_ENV=testing and DEV_DATABASE_URI
- In this mode **Initial Data are loaded**

#### Mock files used

- `backend/testing/data/systems.json`
- `backend/testing/data/dht/<home_uuid>/domo_room.json`
- `backend/testing/data/dht/<home_uuid>/domo_light.json`
- `backend/testing/data/dht/<home_uuid>/domo_light_dimmable.json`
- `backend/testing/data/dht/<home_uuid>/domo_rgbw_light.json`
- `backend/testing/data/dht/<home_uuid>/domo_switch.json`
- `backend/testing/data/dht/<home_uuid>/domo_roller_shutter.json`
- `backend/testing/data/dht/<home_uuid>/domo_camera.json`
- `backend/testing/data/dht/<home_uuid>/privacy_rule.json`

#### Notes

- Data Subject login does not call Smartotum auth endpoint.
- Smartotum systems/rooms/devices/rules are read from `backend/testing/data`.
- Rule create/delete are applied in-memory during process lifetime (initial state loaded from `privacy_rule.json`).
- Application sync still uses `SMARTOTUM_APPLICATIONS_JSON`.
- After login, call `POST /api/homes/refresh` to load mocked homes into the local database.

### RUN IN DEMO

- In demo mode only 1 container is created that contains all the components of the application
- In this mode **Initial Data are loaded**

#### Start full stack (demo)

```bash
docker compose --env-file .env -f docker/docker-compose-demo.yml up -d --build
docker compose --env-file .env -f docker/docker-compose-demo.yml down -v #to destroy it
```

- env variables that are important in demo phase

```ini
FLASK_ENV=demo
DEMO_DATABASE_URI=postgresql+psycopg2://<user>:<password>@postgres:5432/privacy_db #when FLASK_ENV=demo
VITE_API_BASE_URL=/api/
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

The app is reachable at `http://localhost:5050` (frontend) and `http://localhost:5050/docs/swagger` (API docs).

## Endpoints

- **Swagger UI / OpenAPI docs:** `http://localhost:5050/docs/swagger`
- **Login:** `POST /api/auth/login` (sets `st_access_token` / `st_refresh_token` cookies)
- **Smartotum homes:** `GET /api/homes` (requires the access-token cookie; maps data from Smartotum’s `/service/systems` endpoint)

## Marketplace Integration

- The marketplace calls a dedicated endpoint with a backend token to install an application to a Data Controller
- The corrisponding Data Controller will be set as the owner
- Other delegate can be added but they will only be applied the first time the application is added
- This flow does not use user cookies/JWT login.

### Endpoint

- `POST /api/integrations/marketplace/apps`
- Header: `Authorization: Bearer <MARKETPLACE_INGEST_TOKEN>`

### Payload

```json
{
  "id": "com.marketplace.app1", //com.marketplace is required
  "name": "App 1",
  "description": "optional description",
  "owner_email": "controller.marketplace@example.com",
  "delegates_email": [],
  "available_consents": [
    "processing of personal information to provide the service"
  ]
}
```

### Example call

```bash
curl -X POST "http://localhost:5050/api/integrations/marketplace/apps" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MARKETPLACE_INGEST_TOKEN}" \
  -d '{
    "id": "com.marketplace.app1",
    "name": "App1",
    "description": "camera management app",
    "owner_email": "controller.marketplace@example.com",
    "delegates_email": [],
    "available_consents": [
      "processing of personal information to provide the service"
    ]
  }'
```

### Response semantics

- `201 Created`: new application created.
- `204 No Content`: idempotent replay (same app already present with same owner/managers/consents/metadata).
- `401 Unauthorized`: token missing or invalid.
- `404 Not Found`: one or more provided emails do not exist in the dashboard.
- `403 Forbidden`: one or more provided users are not Data Controllers.
- `409 Conflict`: same app id already exists with different owner or different metadata/delegates/consents.