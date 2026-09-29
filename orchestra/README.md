# Orchestra orchestration

Moving the NBA pipeline onto [Orchestra](https://www.getorchestra.io/), running
locally against the `nba_app_backend` container.

| File | What it is |
| --- | --- |
| `nba_dbt_pipeline.yml` | The dbt half — staging → intermediate → marts → semantic views. |
| `nba_collect_pipeline.yml` | The API half — collect a season, then load it to Postgres. |
| `nba_gcp_pipeline.yml` | All-cloud: collect → GCS → BigQuery → dbt, as one DAG. |
| `nba_task.py` | Standalone collect / load steps — no API, no web server, no JWT. |
| `requirements-task.txt` | Slim deps for `nba_task.py` on Orchestra's Python runner. |
| `run_local.py` | Executes those YAMLs locally, because Orchestra has no local engine. |
| `cli.sh` | `orchestra-cli` wrapper — picks the 3.12 venv, reads the API key from `.env`. |

## The one thing to know first

**Orchestra cannot run this pipeline locally.** It is a hosted control plane.
`orchestra-cli pipeline validate` is the one command usable without an account —
it POSTs to a public schema endpoint, so it needs internet but no API key. Every
command that *executes* something needs `ORCHESTRA_API_KEY`, and the dbt Core task
then runs on Orchestra's infrastructure. From there it can reach neither `nba_dataset.duckdb`
on your laptop nor the `postgres-host` compose service.

So there are two separate things, and both are set up:

1. **Local demo** — `run_local.py` runs the pipeline's DAG in your container. No
   Orchestra account needed. This is what to use day to day.
2. **Real Orchestra** — the same YAML, registered with `orchestra-cli` so it shows
   up in the control plane. See
   [Linking to your Orchestra account](#linking-to-your-orchestra-account). Being
   *visible* there only needs an API key; being *runnable* needs a git connection
   and a reachable warehouse.

## Local demo

Requires the compose stack up (`nba_app_backend` and `postgres-host`):

```bash
python orchestra/run_local.py
```

```
pipeline: NBA dbt Transform  (orchestra/nba_dbt_pipeline.yml)
inputs:   {'dbt_target': 'container_postgres', 'dbt_command': 'build'}
executor: docker exec nba_app_backend

[1/4] staging.dbt_staging          SUCCEEDED in 4.1s
[2/4] intermediate.dbt_intermediate SUCCEEDED in 2.5s
[3/4] marts.dbt_marts               SUCCEEDED in 9.8s
[4/4] semantic_views.dbt_semantic_views SUCCEEDED in 2.7s
pipeline SUCCEEDED - 4 task(s) in 19.0s
```

Useful flags:

```bash
python orchestra/run_local.py --dry-run                      # show the plan, run nothing
python orchestra/run_local.py --select marts                 # one group only
python orchestra/run_local.py --input dbt_command=run        # skip tests
python orchestra/run_local.py --input dbt_target=container   # DuckDB instead of Postgres
```

`run_local.py` reads inputs, `dependsOn` ordering, `paused`, and
`${{ inputs.* }}` substitution from the YAML, and stops the DAG on the first
failure — the same semantics Orchestra applies. It deliberately only understands
`DBT_CORE` / `DBT_CORE_EXECUTE` and errors on any other task type rather than
guessing, so it can't quietly diverge from what Orchestra would do.

### Targets

`pipeline_nba/profiles.yml` gained two container-side targets, because the
existing ones only work from the host:

- **`container_postgres`** (default) — the compose Postgres. `dev` can't be reused
  as-is: its `host: localhost` resolves to the backend container itself, not the
  database.
- **`container`** — the DuckDB file at its in-container path `/nba_app/...`, since
  `local` hardcodes a host path.

Postgres is the default because **DuckDB is missing the `game_schedule` table**,
so `container` fails at `stg_nba_game_schedule` (8 of 9 staging models pass). That
table only lands in DuckDB once collection runs; it is a data gap, not a config
problem.

## The DAG

Four task groups mirroring `pipeline_nba/models/`, so Orchestra renders a real
dependency graph rather than one opaque `dbt build`:

```
staging (8 models) → intermediate (3) → marts (8) → semantic_views (2)
```

Each group is a dbt selector over the same project, so the layering here can't
drift from the `ref()`s in the SQL — dbt still resolves order within a group.

## Linking to your Orchestra account

Everything below runs through `orchestra/cli.sh`, which picks the right venv and
reads `ORCHESTRA_API_KEY` from `.env` (gitignored) so you don't have to export it.

### 1. Add your API key

Generate one in Orchestra's app settings, then append it to `.env`:

```bash
echo 'ORCHESTRA_API_KEY=your_key_here' >> .env
```

### 2. Create the pipeline

```bash
./orchestra/cli.sh pipeline new -a nba_dbt -p orchestra/nba_dbt_pipeline.yml --publish
```

This uploads the local YAML as an **Orchestra-backed** pipeline — no git
connection needed — and prints an edit URL. It's now visible in the control plane.

Push later local edits with:

```bash
./orchestra/cli.sh pipeline update -a nba_dbt -p orchestra/nba_dbt_pipeline.yml --publish
./orchestra/cli.sh pipeline list
```

Pass `--publish` on every `update`. It defaults to `--no-publish`, so omitting it
silently unpublishes a pipeline that was published before.

### 3. Migrate to git-backed

Once `usmanalt1/nba_app` is connected in the Orchestra UI, convert the pipeline so
the YAML in git becomes the source of truth:

```bash
./orchestra/cli.sh pipeline migrate -a nba_dbt -p orchestra/nba_dbt_pipeline.yml
```

`migrate` stages, commits and pushes the YAML itself, prompting for the commit
message. Git details are auto-detected — repository `usmanalt1/nba_app`, default
branch `main`, working branch whatever you're on.

(`pipeline import` is the alternative if you'd rather skip the Orchestra-backed
step, but it needs the GitHub connection *and* the YAML pushed first.)

## What's still needed for runs to pass

Being visible in the control plane is not the same as being runnable. The pipeline
is published, so it can be triggered — but runs fail until all of these are done:

1. **A warehouse Orchestra can reach.** The real blocker. The BigQuery profile
   commented out in `profiles.yml` is the natural fit — the GCP service account is
   in the repo and `dbt-bigquery` is installed. Local DuckDB and compose Postgres
   are both dead ends for cloud execution, since Orchestra runs dbt on its own
   infrastructure.
2. **A git connection for the dbt project.** Orchestra's dbt Core integration
   pulls the dbt project from git regardless of how the pipeline YAML got there,
   so this is needed even for an Orchestra-backed pipeline (GitHub PAT with
   `Contents: Read-only`, or a workspace git connection).
3. **A dbt Core connection**, uploading the `profiles.yml` for that warehouse.
   Convenient here: `pipeline_nba/profiles.yml` is gitignored, and Orchestra wants
   it uploaded to the connection rather than committed anyway. Set its
   5-digit-suffixed ID as the `DBT_CORE_CONNECTION` env var — the YAML references
   it as `${{ ENV.DBT_CORE_CONNECTION }}` rather than hardcoding an ID.
4. **A `requirements.txt` pinning dbt** at the repo root for Orchestra's runner.
   The current one is the whole Django app and pins nothing; Orchestra's docs want
   something like `dbt-core==1.10.20` / `dbt-bigquery==1.10.2`.

Until then, `run_local.py` remains the way to actually execute the pipeline.

Add a `schedule:` block to the YAML for cron (the schema takes `cron`, `timezone`,
`runInputs`).

### CLI install

The CLI needs **Python 3.10+**, but the project venv is 3.9, where pip silently
resolves to `orchestra-cli` 0.0.4 — whose `run` and `upload` are stubs that print
"Action not supported yet". A separate tools venv avoids that, and `cli.sh` uses
it automatically:

```bash
python3.12 -m venv .venv-orchestra
.venv-orchestra/bin/pip install orchestra-cli
```

## Stage 2: the API in your backend container

[`nba_collect_pipeline.yml`](nba_collect_pipeline.yml) is the API half — collect a
season into object storage, then load it into Postgres:

```
collect (GET /api/nba/collect/season/{season_year}) → load (GET /api/nba/load_to_postgres)
```

Run it the same way as the dbt one:

```bash
python orchestra/run_local.py -p orchestra/nba_collect_pipeline.yml
python orchestra/run_local.py -p orchestra/nba_collect_pipeline.yml --input season_year=2023-24
```

It's a separate file rather than four extra groups on the front of the dbt
pipeline, so each half stays independently runnable and the fast dbt demo is still
one command. To chain them: in Orchestra, add a `triggerEvents` entry on the dbt
pipeline so it fires when this one completes; locally, run the two scripts in
sequence.

### Credentials

The API router is behind JWT auth (`AsyncJWTAuth`), so HTTP tasks need a token.
Add either form to `.env`:

```bash
NBA_API_TOKEN=eyJ...
# or, and run_local.py exchanges these at /api/token/pair:
NBA_API_USERNAME=admin
NBA_API_PASSWORD=...
```

### How the HTTP task is shaped

Orchestra's `HttpParametersModel` is deliberately minimal — `path`, `method`, and
an optional **string** `body`. There is no URL, headers or auth field:

```yaml
integration: HTTP
integrationJob: HTTP_REQUEST
connection: ${{ ENV.NBA_API_CONNECTION }}
parameters:
  path: /api/nba/collect/season/${{ inputs.season_year }}
  method: GET
```

The host and the `Authorization` header live in the Orchestra **HTTP connection**,
which is why the YAML carries no base URL. Locally, `run_local.py` supplies both:
`--base-url` (default `http://localhost:8000`) and a token from `.env`.

## Where it runs, and the plan limits

Python and dbt tasks execute on **Orchestra's own AWS infrastructure**, in a private
subnet in `eu-west-2` (the documented whitelist IPs — 13.41.17.109, 13.42.169.51,
18.168.251.89 — are London ranges, and there are additional dedicated IPs for the dbt
and Python integrations specifically). Your repo is cloned onto their runner and the
command runs there. Nothing runs on your machine or in your GCP project.

Worth being deliberate about: Orchestra's security page says it has "access to
underlying data applications but not the underlying data". That describes its metadata
collection, and it does not hold for a Python task — you hand the runner a GCP
service-account key as a secret, so their compute can read and write your bucket and
dataset for the length of the run. If that is not acceptable, run the same script in
your own account instead: `GCP_CLOUD_RUN_EXECUTE_JOB`, `AWS_ECS` or
`AZURE_CONTAINER_APPS` all keep the compute (and the key) on your side, and
`nba_task.py` needs no changes for that.

### Plan limits

This account is on **LEAN (free)**, confirmed by the API rejecting a 4th pipeline:

```
The number of pipelines (4) exceeds the limit of 3 pipelines per account.
```

| | LEAN ($0) | SCALE-UP ($150/user/mo, 2–5 users) |
| --- | --- | --- |
| Users | 1 | 2–5 |
| Pipelines | **3** | unlimited |
| Environments | 1 | 2 |
| Compute minutes/day | **30** | 500 |
| Tasks/day | **24** | 500 |

Plus an undocumented **5 tasks per pipeline** cap on this account, which is why the
dbt groups in `nba_gcp_pipeline.yml` were collapsed into one `dbt build`.

**The three published pipelines already use the whole pipeline allowance** — a fourth
is rejected. Delete one, or reuse an alias with `pipeline update`, before adding more.

On SCALE-UP the minimum is 2 users, so the real floor is **$300/month**, not $150.

### What that means for this pipeline

`nba_gcp` is 3 tasks per run, so **24 tasks/day caps it at 8 runs/day**, and that will
bind before compute minutes do for normal runs. Rough per-run estimate (not measured —
no full collect has been run):

| Step | Estimate | Why |
| --- | --- | --- |
| collect, 1 season | ~2–5 min | `_get_team_matchups` loops all 30 teams with 2 nba_api calls and a `t.sleep(1)` each |
| load to BigQuery | ~1 min | one `load_table_from_dataframe` per table |
| `dbt build` | ~1–3 min | 21 models plus tests, on BigQuery |

So a daily scheduled run fits the free tier comfortably. What will not fit is
backfilling: `--seasons 5` multiplies the collect step by five and would consume most
of a day's 30 minutes in one run. Backfill locally with `run_local.py` instead, where
compute is free.

## Connections

Queried from `/api/engine/public/integrations/<INTEGRATION>` — none exist on the
account yet (`/integrations/connections` returns `[]`).

**There is no separate "git connection" to create.** Both the dbt Core and Python
connections carry their own repo config, and `auth_method` chooses how they
authenticate:

- `TOKEN` — paste a PAT into each connection
- `GIT_CONNECTION` — use a workspace-level git connection set up once in the UI, then
  referenced by both. Fewer places for a token to expire.

### dbt Core — `DBT_CORE_CONNECTION`

| Field | Required | Value here |
| --- | --- | --- |
| `repo_source` | yes | `GITHUB` |
| `repo_path` | yes | `usmanalt1/nba_app` |
| `auth_method` | yes | `TOKEN` or `GIT_CONNECTION` |
| `token` | if `TOKEN` | GitHub PAT, `Contents: Read-only` |
| `profiles_yaml` | yes | paste `pipeline_nba/profiles.yml` — it's gitignored, so Orchestra can't read it from the repo |
| `secrets` | no | Secret JSON, if you'd rather not have credentials inside `profiles.yaml` |

`profiles_yaml` being a connection field is why the gitignored `profiles.yml` is not
a problem — Orchestra wants it pasted, not committed.

### Python — for the `nba_gcp` collect and load tasks

Same fields **minus `profiles_yaml`**: `repo_source`, `repo_path`, `auth_method`,
`token`, and `secrets`.

Put the service-account key in `secrets`:

```json
{ "GCS_SERVICE_ACCOUNT_JSON_CONTENT": "{\"type\":\"service_account\",\"project_id\":\"nba-ua-dev\", ...}" }
```

Secrets export as environment variables and are redacted in logs. `nba_task.py`
writes that content to a temp file and repoints `GCS_SERVICE_ACCOUNT_JSON` at it.
Everything non-secret is already in the task's `environment_variables`.

**What the Python connection actually connects to: your GitHub repo, nothing else.**
It is not a connection to a database or an API. Per Orchestra's own setup guide, its
prerequisites are just "a repository with Python code" and "an authorization token
for your chosen Git provider". It does two jobs — tells the runner what to clone, and
carries secrets to export as env vars.

That is why a `source: GIT` task needs one: the repo path and token live there and
nowhere else. Both Python tasks in `nba_gcp_pipeline.yml` reference it as
`${{ ENV.PYTHON_CONNECTION }}`.

Secrets must be strings, numbers or booleans. For anything structured the guide says
to "store a JSON string and then parse it in your Python code" — which is exactly
what `GCS_SERVICE_ACCOUNT_JSON_CONTENT` is.

### HTTP — `NBA_API_CONNECTION` (only for `nba_collect`)

`base_url`, `auth_type`, then whichever of `username`/`password`,
`bearer_token`, or `header_key`/`header_value` that auth type needs. `base_url` is
why the YAML carries only a `path`.

Not needed for `nba_gcp`, which has no HTTP tasks.

### One warning

**The GitHub repo is public** — `api.github.com/repos/usmanalt1/nba_app` returns 200
unauthenticated. The gitignored `.env` and `*.json` keyfiles are therefore the only
thing keeping those credentials out of public view. When the runner can't find them,
the tempting fix is to commit them. Don't — that publishes them. Use the connection's
`secrets` and the task's `environment_variables`, which is what the setup above does.

## Reaching a local API from Orchestra

The honest answer: **Orchestra's cloud cannot reach `localhost:8000`**, so there
are only three options.

### 1. Don't — run it locally (what's set up)

`run_local.py` executes HTTP tasks directly against the container. Nothing is
exposed, and the YAML stays byte-identical to what Orchestra would run. Best for
development and demos.

### 2. Tunnel the container

For Orchestra's cloud to call your laptop, the API needs a public URL:

```bash
cloudflared tunnel --url http://localhost:8000     # or: ngrok http 8000
```

Then create an HTTP connection in Orchestra with that URL as the base and an
`Authorization: Bearer <token>` header.

Worth being clear-eyed about: this publishes a dev backend to the internet, the
URL changes on every restart, and the JWT is the only thing in front of it. Fine
for a one-off demo, not something to leave running.

### 3. Deploy the API

The real answer for production — any internet-reachable host. This also solves the
warehouse problem, since dbt can then point at the same deployment's database
rather than BigQuery.

## Two traps worth knowing

**1. Orchestra will report a failed collection as SUCCEEDED.** These endpoints
return HTTP **200** with `{"success": false, "error": ...}` on failure — see
[api.py:131](../backend/src/api/api.py#L131). Orchestra's HTTP task only fails on a
non-2xx status, so it goes green and dbt then transforms stale data.
`run_local.py` parses the body and fails on `success: false`; Orchestra cannot,
until the endpoints return a 4xx/5xx status. Verified:

```
HTTP 200: {"success": false, "error": "invalid literal for int()..."}
reported success=false: invalid literal for int()...
FAILED
```

**2. Don't orchestrate the multi-season endpoint as-is.**
`/collect/season/{season_year}/{seasons}/team_roster={team_roster}` fires
`asyncio.create_task(...)` and responds before collection finishes — see
[api.py:166](../backend/src/api/api.py#L166). Any orchestrator would mark it
complete immediately.

The pipeline therefore uses the single-season endpoint
([api.py:110](../backend/src/api/api.py#L110)), which `await`s its work properly,
as does `/load_to_postgres`. For multiple seasons, either await the multi-season
endpoint instead of detaching it, or wrap the collect group in an Orchestra
`matrix` over a list of seasons — which also gets you per-season retries and
parallelism.

The existing Dagster assets in [dagster/assets.py](../dagster/assets.py) cover the
same collect → load steps and are worth reading as a reference.

## The all-cloud architecture (GCS → BigQuery → dbt)

**Yes, Orchestra can do this — and it's the version that removes every blocker
above**, because nothing stays on your laptop. [`nba_gcp_pipeline.yml`](nba_gcp_pipeline.yml)
is that pipeline, one DAG of six nodes:

```
collect ──> load ──> staging ──> intermediate ──> marts ──> semantic_views
(to GCS)   (to BQ)   └──────────── dbt, --target bigquery ────────────┘
```

You are most of the way there already — the code for every step exists:

| Step | What runs it | Status |
| --- | --- | --- |
| Collect → GCS | `GCSStorage` in [object_storage/service.py](../backend/src/services/object_storage/service.py) | Written; needs `STORAGE=gcs` |
| GCS → BigQuery | `load_latest_data_from_gcs_to_bigquery` in [bigquery/service.py](../backend/src/services/warehouse_storage/bigquery/service.py) | Written; blocked by a wrong project (below) |
| dbt on BigQuery | the new `bigquery` target in `profiles.yml` | **Verified** — `dbt debug` passes against `nba-ua-dev` |

### Fixed while checking this

- **`profiles.yml` gained a real `bigquery` target.** The commented-out one pointed
  at project `nbaprediction-489613` with `nbaprediction_service_account.json` — a
  different GCP project that does not hold this data. The new target uses
  `nba-ua-dev` with the matching keyfile. `dbt debug --target bigquery` passes.
- **`src_nba.yml` resolves the source dataset per adapter.** It only distinguished
  DuckDB (`test`) from everything else (`public`); on BigQuery the "schema" is the
  dataset, so dbt would have looked for a dataset called `public`. It now resolves
  to `BIGQUERY_DATASET_ID` (`nba_dataset`), overridable with
  `--vars '{raw_dataset: other}'`.
- **`dbt-bigquery` added to `requirements.txt`.** It was missing, so the container
  could not use a BigQuery target at all (`Could not find adapter type bigquery`).

### Still to fix: `GCS_PROJECT_NAME` is wrong

`.env` sets `GCS_PROJECT_NAME=nba-app-dev`, but **that project does not exist**:

```
GCS  project=nba-app-dev      bucket -> FOUND      (bucket names are global, so this works by luck)
BQ   project=nba-app-dev      ERROR NotFound: 404 .../projects/nba-app-dev/datasets
BQ   project=nba-ua-dev       datasets -> ['features_dev','intermediate_dev','marts_dev','raw_dev','staging_dev']
```

GCS writes succeed because bucket names are globally unique and the project is only
used for billing. BigQuery is project-scoped, so `load_to_bigquery` fails. Set
`GCS_PROJECT_NAME=nba-ua-dev` — which is also what the `nba-ua-dev` service account
is scoped to.

Note the existing datasets are `raw_dev` / `staging_dev` / `marts_dev`, while
`BIGQUERY_DATASET_ID` is `nba_dataset`. Decide which convention wins before the
first real load, or you'll end up with both.

### Why this architecture is the answer

Every problem called out earlier dissolves:

| Problem | Why it goes away |
| --- | --- |
| Orchestra can't reach local DuckDB/Postgres | dbt targets BigQuery, which is cloud-native |
| Orchestra can't reach `localhost:8000` | collect runs in GCP, not on your laptop |
| Needs a tunnel | none — nothing inbound to your machine |

### collect runs as a standalone script, not an API call

No API, no web server, no JWT, no tunnel. Orchestra clones the repo and runs
[`nba_task.py`](nba_task.py) directly with a `PYTHON` task:

```yaml
integration: PYTHON
integrationJob: PYTHON_EXECUTE_SCRIPT
parameters:
  source: GIT
  project_dir: .
  build_command: pip install -r orchestra/requirements-task.txt
  command: python orchestra/nba_task.py collect --season-year ${{ inputs.season_year }} --seasons ${{ inputs.seasons }}
```

`PythonExecuteScriptParametersModel` takes `command`, `source` (`GIT` or `INLINE`),
`project_dir`, `python_version` and `build_command`.

The same file runs the load step, and both work identically from a shell — which is
how they were tested:

```bash
python orchestra/nba_task.py collect --season-year 2024-25 --seasons 3
python orchestra/nba_task.py load-bigquery --seasons 2024-25
```

**This is what makes the pipeline trustworthy.** The script has no
exception-swallowing layer: it raises, exits non-zero, and the DAG stops. Verified
with a deliberately bad season — `collect` failed and none of the five downstream
tasks ran:

```
[1/6] collect.collect_season
  ValueError: season_year must look like '2024-25', got 'not-a-season'
  FAILED in 1.1s (exit 1)
pipeline FAILED at collect.collect_season
```

The HTTP equivalent would have returned 200, and all six tasks would have gone
green. `run_local.py` also runs `PYTHON` tasks, so the whole DAG is testable
locally.

Three things made this possible:

- **The collect path is now Django-free.** `build_data_service.py` imported
  `django.utils.timezone` and `app.models.PlayerAwards` at module scope, but only
  `build_player_awards` uses them — they moved inside that method. `build_nba_data`
  now needs no `django.setup()` and no database, so the script and its dependency
  list stay small. `manage.py check` passes.
- **`requirements-task.txt`** pins just the collect/load deps at the versions the
  container runs. The root `requirements.txt` would drag in Django, mysqlclient
  (needs system libraries a bare runner lacks), snowflake-snowpark, scikit-learn and
  the dbt adapters.
- **`nba_task.py` reproduces the API's season-id arithmetic exactly** (`"2024-25"` →
  `"24025"`), verified identical across five seasons back, so both paths collect the
  same data. It derives the id from the year each iteration rather than decrementing
  two strings in parallel, which is what the API does.

If you would rather not have Orchestra clone the repo, the same script runs
unchanged as a Cloud Run job (`GCP_CLOUD_RUN_EXECUTE_JOB`, needs `job_name`) —
that is a packaging change, not a code change. `GCP_CLOUD_FUNCTIONS_EXECUTE_ASYNC_FUNCTION`
and `GKE_RUN_JOB` also exist.

### Where the scripts actually run

On **Orchestra's own managed compute** — a fresh, ephemeral runner, not your machine
and not GCP. For each `PYTHON` task it:

1. clones the repo (needs a git connection, same one dbt Core uses)
2. `cd`s into `project_dir`
3. runs `build_command` (`pip install -r orchestra/requirements-task.txt`)
4. runs `command` — only commands starting with `python`, `poetry` or `uv` are allowed

Constraints worth knowing:

| | |
| --- | --- |
| Python version | **3.11 or 3.12 only.** `"3.9"` is rejected by the schema — the backend container is 3.9, so `nba_task.py` must work on both. It sticks to stdlib `argparse`/`logging`. |
| Package manager | `PIP`, `POETRY` or `UV` |
| Auto-injected | `ORCHESTRA_API_KEY`, `ORCHESTRA_PIPELINE_RUN_ID`, `ORCHESTRA_TASK_RUN_ID`, `ORCHESTRA_WEBHOOK_URL`, …; `orchestra-sdk` is installed for you |
| Secrets | Set on the Python connection, exported as env vars, redacted in logs |
| Big repos | `shallow_clone_dirs` limits what is cloned. Not needed here: the heavy things in the working tree (`node_modules`, the 12 MB DuckDB file, the parquet folders) are all gitignored, and the largest tracked file is 18 KB |

### The trap this creates, and the fix

**`.env` and the service-account JSON are both gitignored**, so neither exists in the
repo Orchestra clones. Left alone, `config/settings.py` falls back to its defaults —
including `STORAGE = "local"` — and `ObjectStorageService` silently returns
`LocalStorage`. Collect would write parquet to an ephemeral disk that is discarded
when the task ends, **and report success**.

Three things now prevent that:

- **`environment_variables`** on each task carries `STORAGE`, `PARENT_BUCKET`,
  `GCS_PROJECT_NAME`, `FILE_FORMAT` and `BIGQUERY_DATASET_ID`. It must be a JSON
  *string*, not a mapping — a mapping is rejected. `pydantic-settings` reads real env
  vars before `env_file`, so this wins.
- **`GCS_SERVICE_ACCOUNT_JSON_CONTENT`** — set the key's JSON as a secret on the
  Python connection. The services want a *path* (`from_service_account_json`,
  `gcsfs(token=...)`), so `nba_task.py` writes the content to a temp file and
  repoints `GCS_SERVICE_ACCOUNT_JSON` at it. Nothing in `services/` changed.
- **`--expect-storage gcs`** fails the task if the resolved backend isn't the one you
  meant. Verified:

```
object storage backend: LocalStorage (STORAGE=)
RuntimeError: --expect-storage gcs requires GCSStorage, but resolved LocalStorage.
  STORAGE='' - on a cloud runner .env is not in the repo, so STORAGE must be passed
  as an environment variable.
exit=1
```

`load-bigquery` asserts `gcs` even without the flag, because `BigQueryService` reads
`.storage_client` off the backend and only `GCSStorage` has one — previously that
surfaced as an opaque `AttributeError` partway in.

### The `success: false` trap, and why this pipeline dodges it

`nba_collect_pipeline.yml` uses HTTP tasks, and those endpoints return **HTTP 200**
with `{"success": false, "error": ...}` on failure. Orchestra fails a task only on a
non-2xx status, so a silently failed collect would still mark `load` and all four
dbt groups runnable — dbt then transforms last week's data and reports success.

`nba_gcp_pipeline.yml` avoids this by not going through the API at all. The trap
still applies to the HTTP pipeline and to anything else calling those endpoints, so
**they should return 4xx/5xx** regardless — that is a one-line change per handler
and it makes them orchestratable by anything, not just this runner.
