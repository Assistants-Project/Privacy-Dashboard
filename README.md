# Privacy Dashboard

## Docker

This repository provides:

- `docker-compose.yml`: PostgreSQL only, used only when developing so Database,Backend and Frontend can be launched separately
- `docker-compose.deploy.yml`: full stack solution for testing/demo, it includes: frontend + backend + PostgreSQL, when using this flask is in testing mode

### Prerequisites

- Docker and Docker Compose
- Python 3.11 or newer (with `pip`)

### Configure environment variables

- Create a `.env` file in the repository root
- Accurately set the env according to your needs (development|testing|production)

```ini
#FLASK
FLASK_ENV=development #development|testing|production
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
DEV_DATABASE_URI=postgresql+psycopg2://<user>:<password>@localhost:5434/privacy_db #when FLASK_ENV=development
TEST_DATABASE_URI=postgresql+psycopg2://<user>:<password>@postgres:5432/privacy_db #when FLASK_ENV=testing
DATABASE_URI=postgresql+psycopg2://<user>:<password>@<host>:<port>/privacy_db #when FLASK_ENV=production

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
MARKETPLACE_APPLICATIONS_JSON=./config/marketplace-apps.json

#ONTOLOGY
ONTOLOGY_DIRECTORY=app/ontologies/
ONTOLOGY_BASE_ENDPOINT=https://elite.polito.it/ontologies/eupont.owl
ONTOLOGY_SIFIS_FILE=sifis-home.owl

#REASONER
REASONER_TYPE=hermit
REASONER_PRECOMPUTE_INFERENCES=True

#POLICIES
POLICIES_DIRECTORY=data/policies/

#TEMPLATES/SCHEMAS
PRIVACY_NOTICE_TEMPLATE_PATH=./config/privacy-notice-template.json
PIA_TEMPLATE_PATH=./config/privacy-impact-assessment-template.json
PIA_SCHEMA_PATH=./config/privacy-impact-assessment-schema.json

#FRONTEND

#VITE
VITE_API_BASE_URL=http://localhost:5050/api/ #choose same port as the one in flask run --port
VITE_API_BASE_UR= /api/ #when frontend is built in testing

#CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173 #works for both development and testing, chose the same port where the vite frontend is running
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

### RUN IN TESTING

- In testing/demo mode only 1 container is created that contains all the components of the application
- In this mode **Initial Data are loaded**

#### Start full stack (testing/demo)

```bash
docker compose --env-file .env -f docker/docker-compose.deploy.yml up -d --build
docker compose --env-file .env -f docker/docker-compose.deploy.yml down -v #to destroy it
```

- env variables that are important in testing phase

```ini
FLASK_ENV=testing
TEST_DATABASE_URI=postgresql+psycopg2://<user>:<password>@postgres:5432/privacy_db #when FLASK_ENV=testing
VITE_API_BASE_UR= /api/
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

The app is reachable at `http://localhost:5050` (frontend) and `http://localhost:5050/docs/swagger` (API docs).

## Endpoints

- **Swagger UI / OpenAPI docs:** `http://localhost:5050/docs/swagger`
- **Login:** `POST /api/auth/login` (sets `st_access_token` / `st_refresh_token` cookies)
- **Smartotum homes:** `GET /api/homes` (requires the access-token cookie; maps data from Smartotum’s `/service/systems` endpoint)
