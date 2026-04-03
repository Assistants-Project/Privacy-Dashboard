# Performance Benchmarks

The repository includes lightweight benchmark helpers under `scripts/benchmarks/`.
They are intended to support thesis measurements with repeatable commands and JSON/CSV/TXT output.

Run all commands below from the repository root.

## Recommended setup

1. Start the backend in `testing` mode if you want a reproducible local harness:

```bash
source .venv/bin/activate
bash scripts/reset_postgres_and_run.sh testing
```

When started in `testing`, the reset script also deletes `backend/testing/data/dht/**/_output.json` files so the DHT mock starts from the base fixtures instead of a previously mutated output state.

2. Run the benchmark scripts from another shell.

Important notes:

- `testing` mode is useful to validate the benchmark harness, but DHT/Smartotum latency numbers are **not representative** because the DHT is mocked in memory.
- For `policy propagation latency`, run the same script against a real/demo deployment with actual Smartotum connectivity to obtain real numbers.
- The API collection benchmark uses Dockerized Newman; when the backend runs on the host, `host.docker.internal` is usually the correct base URL on macOS/Windows.
- When `--ds-password` is omitted, the benchmark scripts use a testing-only fallback password for the Data Subject. This works only with `FLASK_ENV=testing`; in `development` or `demo`, pass the real Smartotum password explicitly.
- The examples below intentionally show all value-bearing parameters exposed by each benchmark script. Boolean toggle flags are listed separately under each example.

## Run All Benchmarks

If you want a single command that launches all benchmark scripts, saves every per-benchmark `json/csv/txt`, and also generates a final `summary.txt`, use:

```bash
python3 scripts/benchmarks/run_all_benchmarks.py \
  --output-dir scripts/benchmarks/results \
  --base-url http://127.0.0.1:5050 \
  --api-collection-base-url http://host.docker.internal:5050 \
  --ds-email s312192@studenti.polito.it \
  --ds-password 'smartotum_password_ds' \
  --withdraw-application-id com.smartotum.smartotum-camera-manager \
  --withdraw-consent-content 'Consent to Record Video Footage from Smart Home Cameras' \
  --withdraw-iterations 10 \
  --withdraw-warmup 2 \
  --withdraw-settle-timeout 10.0 \
  --withdraw-poll-interval 0.2 \
  --translation-iterations 30 \
  --translation-warmup 5 \
  --translation-multi-subject-count 3 \
  --petrinet-rule-counts 10 25 50 \
  --petrinet-iterations 50 \
  --petrinet-warmup 10 \
  --petrinet-conflict-type inconsistency \
  --owl-ontology-directory backend/app/ontologies/ \
  --owl-ontology-file sifis-home.owl \
  --owl-iterations 10 \
  --owl-warmup 2 \
  --api-collection backend/testing/tests/Privacy-Dashboard-API.postman_collection_cleaned.json \
  --api-iterations 3 \
  --dc-email controller.smartotum@example.com \
  --dc-password controllersmartotum \
  --delegate-email controller.general@example.com \
  --dpo-email dpo.general@example.com \
  --dpo-password dpogeneral \
  --marketplace-integration-token 'BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4' \
  --dc-updated-password controllersmartotum-updated \
  --dpo-updated-email dpo.general.updated@example.com \
  --dpo-updated-password dpogeneral-updated
```

By default, the wrapper executes the benchmarks in this order: `api`, `withdraw`, `translation`, `petrinet`, `owl`.

Important parameters:

- `--output-dir`: optional. If omitted, the script writes directly into `scripts/benchmarks/results`. Re-running the wrapper overwrites the benchmark artifacts with the same filenames in that directory.
- `--benchmarks`: optional. Lets you run only a subset, for example `--benchmarks withdraw translation` or `--benchmarks petrinet`.
- `--base-url`: optional, used by the withdraw and translation benchmarks.
- `--api-collection-base-url`: optional, used only by the Newman benchmark and must be reachable from inside the Docker container.
- `--home-uuid`: optional. If omitted, the withdraw and translation benchmarks use the first available home.
- `--ds-password`: optional only in `testing`. If omitted, the wrapper forwards the same testing-only fallback behavior used by the individual scripts.
- `--skip-refresh`: optional flag. If set, the wrapper forwards `--skip-refresh` to the withdraw and translation benchmarks.
- `--owl-ontology-directory`: optional, forwarded to the OWL loading benchmark.
- `--owl-ontology-file`: optional, forwarded to the OWL loading benchmark.
- `--owl-suppress-reasoner-output` / `--no-owl-suppress-reasoner-output`: optional boolean flag, default enabled. Controls whether the wrapper passes `--suppress-reasoner-output` to the OWL loading benchmark.
- `--api-success-only` / `--no-api-success-only`: optional boolean flag, default enabled. Controls whether the wrapper passes `--success-only` to the API collection benchmark.

The output directory will contain:

- `withdraw-latency.json`, `withdraw-latency.csv`, `withdraw-latency.txt`
- `translation-benchmark.json`, `translation-benchmark.csv`, `translation-benchmark.txt`
- `petrinet-benchmark.json`, `petrinet-benchmark.csv`, `petrinet-benchmark.txt`
- `owl-loading-benchmark.json`, `owl-loading-benchmark.csv`, `owl-loading-benchmark.txt`
- `api-benchmark.json`, `api-benchmark.csv`, `api-benchmark.txt`
- `summary.txt`

## 1. Policy Propagation Latency

Measures the time from `POST /api/requests/submit` with `WITHDRAW_CONSENT` to the first observation of new deny-rule UUIDs through the DHT proxy endpoint.

By default, the benchmark is pinned to the Smartotum camera manager application
`com.smartotum.smartotum-camera-manager` and to the mapped consent
`Consent to Record Video Footage from Smart Home Cameras`, as defined in
`backend/config/smartotum-apps.json`. You can override both values with
`--application-id` and `--consent-content`.

```bash
python3 scripts/benchmarks/benchmark_withdraw_latency.py \
  --base-url http://127.0.0.1:5050 \
  --ds-email s312192@studenti.polito.it \
  --ds-password 'smartotum_password_ds' \
  --application-id com.smartotum.smartotum-camera-manager \
  --consent-content 'Consent to Record Video Footage from Smart Home Cameras' \
  --iterations 10 \
  --warmup 2 \
  --settle-timeout 10.0 \
  --poll-interval 0.2 \
  --json-out scripts/benchmarks/results/withdraw-latency.json \
  --csv-out scripts/benchmarks/results/withdraw-latency.csv \
  --txt-out scripts/benchmarks/results/withdraw-latency.txt
```

Parameters:

- `--base-url`: optional, default `http://127.0.0.1:5050`. If you pass the backend root URL without `/api`, the script appends `/api` automatically.
- `--ds-email`: optional, default `s312192@studenti.polito.it`.
- `--ds-password`: optional only in `testing`. If omitted, the script tries the testing-only fallback password. In `development` or `demo`, pass the real Smartotum password explicitly.
- `--application-id`: optional, default `com.smartotum.smartotum-camera-manager`. This is matched against the installed application name returned by `GET /api/applications/home/<home_uuid>`.
- `--consent-content`: optional, default `Consent to Record Video Footage from Smart Home Cameras`. The script searches for this consent content inside the selected application and requires a non-null `sifis_action_id`.
- `--home-uuid`: optional. If omitted, the script calls `GET /api/homes` and uses the first available home for the authenticated Data Subject.
- `--iterations`: optional, default `10`. Must be `>= 1`. These are the measured runs.
- `--warmup`: optional, default `2`. Must be `>= 0`. Warmup runs are executed before measured runs and excluded from the reported stats.
- `--settle-timeout`: optional, default `10.0`. Maximum number of seconds to wait for DHT rule appearance and cleanup.
- `--poll-interval`: optional, default `0.2`. DHT polling interval in seconds while waiting for rule creation/removal. The first DHT check happens immediately after the withdraw request returns; this value applies only to subsequent polling cycles if the rule is not yet visible.
- `--skip-refresh`: optional flag, default disabled. If omitted, the script refreshes homes and applications before starting.
- `--keep-withdrawn-state`: optional flag, default disabled. If omitted, the script re-grants the consent and waits for DHT cleanup after each run.
- `--json-out`: optional. If omitted, no JSON report is written.
- `--csv-out`: optional. If omitted, no CSV report is written.
- `--txt-out`: optional. If omitted, no human-readable text report is written. When provided, the script saves the same readable summary shown in the terminal to a plain-text file.

## 2. PTP Translation Time

Measures XACML translation through the Flask endpoint `POST /api/sifis/homes/<home_uuid>/rules/<rule_id>/download` for:

- a simple deny rule
- a temporal deny rule
- a multi-subject surrogate batch (the current data model supports a single string subject, not a true subject list)

About the multi-subject surrogate scenario:

- the current rule model supports only one `subject` per rule, so the benchmark cannot create a true single rule with multiple subjects inside it
- instead, the script creates multiple equivalent rules, each with a different subject, and translates all of them through the same Flask endpoint
- this is still an end-to-end endpoint benchmark, not a direct function-level microbenchmark
- `multi_subject_surrogate batch` in the reports means the total time needed to translate the whole group of generated per-subject rules
- `multi_subject_surrogate per-rule` means the average end-to-end cost for a single translated rule inside that same batch
- the scenario is therefore an approximation of “multiple subjects to translate”, not a native multi-subject rule supported by the current data model

```bash
python3 scripts/benchmarks/benchmark_translation.py \
  --base-url http://127.0.0.1:5050 \
  --ds-email s312192@studenti.polito.it \
  --ds-password 'smartotum_password_ds' \
  --iterations 30 \
  --warmup 5 \
  --multi-subject-count 3 \
  --json-out scripts/benchmarks/results/translation-benchmark.json \
  --csv-out scripts/benchmarks/results/translation-benchmark.csv \
  --txt-out scripts/benchmarks/results/translation-benchmark.txt
```

Parameters:

- `--base-url`: optional, default `http://127.0.0.1:5050`. If you pass the backend root URL without `/api`, the script appends `/api` automatically.
- `--ds-email`: optional, default `s312192@studenti.polito.it`.
- `--ds-password`: optional only in `testing`. If omitted, the script tries the testing-only fallback password. In `development` or `demo`, pass the real Smartotum password explicitly.
- `--home-uuid`: optional. If omitted, the script calls `GET /api/homes` and uses the first available home for the authenticated Data Subject.
- `--iterations`: optional, default `30`. Must be `>= 1`. These are the measured runs.
- `--warmup`: optional, default `5`. Must be `>= 0`. Warmup runs are executed before measured runs and excluded from the reported stats.
- `--multi-subject-count`: optional, default `3`. Must be `>= 2`. Controls how many per-subject rules are generated for the multi-subject surrogate scenario.
  If omitted, the script still runs the surrogate scenario and generates exactly 3 equivalent rules with different subjects.
- `--skip-refresh`: optional flag, default disabled. If omitted, the script refreshes homes and applications before creating benchmark rules.
- `--json-out`: optional. If omitted, no JSON report is written.
- `--csv-out`: optional. If omitted, no CSV report is written.
- `--txt-out`: optional. If omitted, no human-readable text report is written. When provided, the script saves the same readable summary shown in the terminal to a plain-text file.

## 3. SCPN Conflict Detection Time

Measures `PetriNetService.check_rule()` directly on synthetic rulesets to isolate Petri-net construction and structural conflict detection from HTTP and database overhead.

```bash
python3 scripts/benchmarks/benchmark_petrinet.py \
  --rule-counts 10 25 50 \
  --iterations 50 \
  --warmup 10 \
  --conflict-type inconsistency \
  --json-out scripts/benchmarks/results/petrinet-benchmark.json \
  --csv-out scripts/benchmarks/results/petrinet-benchmark.csv \
  --txt-out scripts/benchmarks/results/petrinet-benchmark.txt
```

Parameters:

- `--rule-counts`: optional, default `10 25 50`. Every value must be `>= 2`. If omitted, the script benchmarks exactly the default curve `10 -> 25 -> 50`.
- `--iterations`: optional, default `50`. Must be `>= 1`. These are the measured runs for each rule-count bucket.
- `--warmup`: optional, default `10`. Must be `>= 0`. Warmup runs are executed before measured runs and excluded from the reported stats.
- `--conflict-type`: optional, default `inconsistency`. Accepted values: `inconsistency`, `redundancy`.
- `--json-out`: optional. If omitted, no JSON report is written.
- `--csv-out`: optional. If omitted, no CSV report is written.
- `--txt-out`: optional. If omitted, no human-readable text report is written. When provided, the script saves the same readable summary shown in the terminal to a plain-text file.
- This script has no `--base-url`, `--home-uuid`, or authentication parameters because it benchmarks the Python service directly.

## 4. API Response Times

Reuses the maintained Postman collection and summarizes response times grouped by normalized HTTP endpoint.
Use `--success-only` to focus on nominal-path latency and exclude regression checks that intentionally return `401`, `403`, or `422`.

```bash
python3 scripts/benchmarks/benchmark_api_collection.py \
  --base-url http://host.docker.internal:5050 \
  --collection backend/testing/tests/Privacy-Dashboard-API.postman_collection_cleaned.json \
  --iterations 1 \
  --success-only \
  --json-out scripts/benchmarks/results/api-benchmark.json \
  --csv-out scripts/benchmarks/results/api-benchmark.csv \
  --txt-out scripts/benchmarks/results/api-benchmark.txt \
  --dc-email controller.smartotum@example.com \
  --dc-password controllersmartotum \
  --ds-email s312192@studenti.polito.it \
  --ds-password 'smartotum_password_ds' \
  --delegate-email controller.general@example.com \
  --dpo-email dpo.general@example.com \
  --dpo-password dpogeneral \
  --marketplace-integration-token 'BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4' \
  --dc-updated-password controllersmartotum-updated \
  --dpo-updated-email dpo.general.updated@example.com \
  --dpo-updated-password dpogeneral-updated
```

Parameters:

- `--base-url`: optional, default `http://host.docker.internal:5050`. This URL must be reachable from inside the Dockerized Newman container. The script does not append `/api`; use the correct value expected by the Postman collection.
- `--collection`: optional, default `backend/testing/tests/Privacy-Dashboard-API.postman_collection_cleaned.json`. If omitted, the maintained collection shipped with the repository is used. If the path does not exist, the script exits.
- `--iterations`: optional, default `1`. Must be `>= 1`. The collection is executed once per iteration and then aggregated by normalized endpoint.
- `--success-only`: optional flag, default disabled. If omitted, the report includes all responses returned by the collection, including expected negative-path checks.
- `--json-out`: optional. If omitted, no JSON report is written.
- `--csv-out`: optional. If omitted, no CSV report is written.
- `--txt-out`: optional. If omitted, no human-readable text report is written. When provided, the script saves the same readable summary shown in the terminal to a plain-text file.
- `--dc-email`: optional, default `controller.smartotum@example.com`.
- `--dc-password`: optional, default `controllersmartotum`.
- `--ds-email`: optional, default `s312192@studenti.polito.it`.
- `--ds-password`: optional only in `testing`. If omitted, the script tries the testing-only fallback password. In `development` or `demo`, pass the real Smartotum password explicitly.
- `--delegate-email`: optional, default `controller.general@example.com`.
- `--dpo-email`: optional, default `dpo.general@example.com`.
- `--dpo-password`: optional, default `dpogeneral`.
- `--marketplace-integration-token`: optional, default `BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4`.
- `--dc-updated-password`: optional, default `controllersmartotum-updated`.
- `--dpo-updated-email`: optional, default `dpo.general.updated@example.com`.
- `--dpo-updated-password`: optional, default `dpogeneral-updated`.
- This script has no `--home-uuid` because the Postman collection derives dynamic identifiers internally during its execution.

The controller layer currently declares `74` routes, and the collection benchmark groups executions by normalized method/path so you can compare observed coverage with the declared API surface.

## 5. OWL Ontology Loading Time

Measures `OWLService` initialization directly to estimate the ontology-loading startup cost of the PTP stack.

This benchmark:

- loads the configured base ontology from disk
- loads the imported EU-PONT ontology
- starts the HermiT reasoner used by the backend OWL service

This benchmark does not include:

- Flask app startup
- Docker container startup
- home ontology regeneration for a specific smart home

```bash
python3 scripts/benchmarks/benchmark_owl_loading.py \
  --ontology-directory backend/app/ontologies/ \
  --ontology-file sifis-home.owl \
  --iterations 10 \
  --warmup 2 \
  --json-out scripts/benchmarks/results/owl-loading-benchmark.json \
  --csv-out scripts/benchmarks/results/owl-loading-benchmark.csv \
  --txt-out scripts/benchmarks/results/owl-loading-benchmark.txt
```

Parameters:

- `--ontology-directory`: optional. If omitted, the script resolves the backend ontology directory from `BaseConfig` and uses `backend/app/ontologies/` when run from the repository root.
- `--ontology-file`: optional, default `sifis-home.owl`. Base ontology file passed to `OWLService`.
- `--iterations`: optional, default `10`. Must be `>= 1`. These are the measured runs.
- `--warmup`: optional, default `2`. Must be `>= 0`. Warmup runs are executed before measured runs and excluded from the reported stats.
- `--suppress-reasoner-output` / `--no-suppress-reasoner-output`: optional boolean flag, default enabled. Controls whether OWLready/HermiT stdout and stderr are silenced during timed initialization.
- `--json-out`: optional. If omitted, no JSON report is written.
- `--csv-out`: optional. If omitted, no CSV report is written.
- `--txt-out`: optional. If omitted, no human-readable text report is written. When provided, the script saves a readable aggregate summary to a plain-text file.

This script has no `--base-url`, `--home-uuid`, or authentication parameters because it benchmarks the Python OWL/PTP bootstrap path directly.
