"""Run an Orchestra pipeline YAML locally, against the nba_app_backend container.

Orchestra itself has no local execution engine - `orchestra-cli` can validate a
pipeline, but running one always happens in Orchestra's cloud, which cannot reach
a DuckDB file on this laptop, the compose Postgres service, or the Django API on
localhost:8000. This script fills that gap for local development: it reads the
*same* YAML that gets imported into Orchestra, resolves the task-group DAG the
same way, and executes each task locally.

It is not a reimplementation of Orchestra - it only understands the task types
this project uses and fails loudly on anything else, so it can't silently diverge
from what Orchestra would do:

  DBT_CORE / DBT_CORE_EXECUTE     `docker exec` into the backend container
  PYTHON   / PYTHON_EXECUTE_SCRIPT  the script, run in the container
  HTTP     / HTTP_REQUEST           an HTTP call to the container's Django API

    python orchestra/run_local.py
    python orchestra/run_local.py -p orchestra/nba_collect_pipeline.yml
    python orchestra/run_local.py --input dbt_target=container_postgres
    python orchestra/run_local.py --select staging --dry-run

HTTP tasks need credentials, because the API router is behind JWT auth. Put them
in .env (gitignored) as either a ready-made token or a username/password this
script exchanges for one at /api/token/pair:

    NBA_API_TOKEN=eyJ...
    # or
    NBA_API_USERNAME=admin
    NBA_API_PASSWORD=...
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PIPELINE = REPO_ROOT / "orchestra" / "nba_dbt_pipeline.yml"

DBT_TASK = ("DBT_CORE", "DBT_CORE_EXECUTE")
HTTP_TASK = ("HTTP", "HTTP_REQUEST")
PYTHON_TASK = ("PYTHON", "PYTHON_EXECUTE_SCRIPT")

INPUT_REF = re.compile(r"\$\{\{\s*inputs\.([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class PipelineError(Exception):
    pass


# --------------------------------------------------------------------------- #
# YAML -> plan
# --------------------------------------------------------------------------- #

def resolve_inputs(declared, overrides):
    """Merge declared input defaults with --input overrides, enforcing `options`."""
    resolved = {}
    for name, spec in (declared or {}).items():
        if name in overrides:
            value = overrides[name]
        elif "default" in spec:
            value = spec["default"]
        elif spec.get("optional"):
            continue
        else:
            raise PipelineError(
                f"input '{name}' has no default and was not passed with --input"
            )
        options = spec.get("options")
        if options and str(value) not in options:
            raise PipelineError(f"input '{name}'='{value}' is not one of {options}")
        resolved[name] = value

    unknown = set(overrides) - set(declared or {})
    if unknown:
        raise PipelineError(
            f"--input referenced undeclared input(s): {', '.join(sorted(unknown))}"
        )
    return resolved


def substitute(text, inputs):
    """Replace ${{ inputs.x }} with its resolved value.

    ${{ ENV.* }} references are left alone - they resolve to Orchestra
    connections, which only exist in the cloud and are irrelevant here.
    """
    def replace(match):
        name = match.group(1)
        if name not in inputs:
            raise PipelineError(f"'{name}' is referenced but not a declared input")
        return str(inputs[name])

    return INPUT_REF.sub(replace, text)


def toposort(nodes):
    """Order {id: [dependency ids]} so dependencies come first."""
    ordered, visiting, done = [], set(), set()

    def visit(node_id, trail):
        if node_id in done:
            return
        if node_id in visiting:
            raise PipelineError(f"dependency cycle: {' -> '.join(trail + [node_id])}")
        visiting.add(node_id)
        for dep in nodes[node_id]:
            if dep not in nodes:
                raise PipelineError(f"'{node_id}' dependsOn unknown id '{dep}'")
            visit(dep, trail + [node_id])
        visiting.discard(node_id)
        done.add(node_id)
        ordered.append(node_id)

    for node_id in nodes:
        visit(node_id, [])
    return ordered


def collect_tasks(pipeline, only=None):
    """Flatten the pipeline into an ordered list of (group_id, task_id, task)."""
    groups = {gid: entry.get("dependsOn", []) for gid, entry in pipeline.items()}

    tasks = []
    for group_id in toposort(groups):
        entry = pipeline[group_id]
        if entry.get("paused"):
            print(f"  skipping paused group '{group_id}'")
            continue

        # A top-level entry is either a task group (has `tasks`) or a bare task.
        group_tasks = entry.get("tasks")
        if group_tasks is None:
            group_tasks = {group_id: entry}

        deps = {tid: t.get("dependsOn", []) for tid, t in group_tasks.items()}
        # Task-level dependsOn may point at sibling tasks or at other groups;
        # cross-group refs are already satisfied by the group ordering above.
        deps = {tid: [d for d in ds if d in deps] for tid, ds in deps.items()}

        for task_id in toposort(deps):
            if only and only not in (group_id, task_id):
                continue
            tasks.append((group_id, task_id, group_tasks[task_id]))
    return tasks


def build_step(task, inputs, container, project_root):
    """Turn one task into a description of what to execute."""
    kind = (task.get("integration"), task.get("integrationJob"))
    params = task.get("parameters") or {}

    if kind == DBT_TASK:
        commands = params.get("commands")
        if not commands:
            raise PipelineError("dbt task is missing parameters.commands")
        # project_dir is relative to the repo root, which is bind-mounted into
        # the container at project_root.
        workdir = f"{project_root}/{params.get('project_dir', '').strip('/')}"
        return {
            "kind": "dbt",
            "command": substitute(commands, inputs),
            "workdir": workdir.rstrip("/"),
            "container": container,
        }

    if kind == PYTHON_TASK:
        command = params.get("command")
        if not command:
            raise PipelineError("Python task is missing parameters.command")
        source = params.get("source", "GIT")
        if source != "GIT":
            raise PipelineError(
                f"only source: GIT is supported locally, got {source!r} - an INLINE "
                "script has no file in the repo to run"
            )
        # build_command is Orchestra installing deps into a fresh runner; the
        # container already has them, so running it here would be pointless churn.
        workdir = f"{project_root}/{params.get('project_dir', '.').strip('./')}"
        return {
            "kind": "dbt",  # same executor: a shell command inside the container
            "command": substitute(command, inputs),
            "workdir": workdir.rstrip("/"),
            "container": container,
        }

    if kind == HTTP_TASK:
        path = params.get("path")
        if not path:
            raise PipelineError("HTTP task is missing parameters.path")
        return {
            "kind": "http",
            "method": params.get("method", "GET").upper(),
            "path": substitute(path, inputs),
            # HttpParametersModel's `body` is a string, not an object.
            "body": substitute(params["body"], inputs) if params.get("body") else None,
        }

    raise PipelineError(
        f"unsupported task type {kind[0]}/{kind[1]} - this runner executes only "
        + ", ".join("/".join(t) for t in (DBT_TASK, PYTHON_TASK, HTTP_TASK))
        + " locally; run it in Orchestra instead"
    )


# --------------------------------------------------------------------------- #
# Execution
# --------------------------------------------------------------------------- #

def read_env_file(path):
    """Parse KEY=VALUE lines out of .env without sourcing it."""
    values = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_api_token(base_url, env):
    """Return a JWT for the API, minting one from username/password if needed.

    Orchestra would hold this in the HTTP connection's headers; locally we have
    to go and get it.
    """
    token = env.get("NBA_API_TOKEN")
    if token:
        return token

    username = env.get("NBA_API_USERNAME")
    password = env.get("NBA_API_PASSWORD")
    if not (username and password):
        raise PipelineError(
            "HTTP tasks need credentials - the API router is behind JWT auth. Set "
            "NBA_API_TOKEN, or NBA_API_USERNAME and NBA_API_PASSWORD, in .env"
        )

    request = urllib.request.Request(
        f"{base_url}/api/token/pair",
        data=json.dumps({"username": username, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
    except urllib.error.HTTPError as exc:
        raise PipelineError(
            f"could not get a token for '{username}' ({exc.code}): {exc.read().decode()[:200]}"
        )
    except urllib.error.URLError as exc:
        raise PipelineError(f"could not reach {base_url}: {exc.reason}")

    access = body.get("access")
    if not access:
        raise PipelineError(f"/api/token/pair returned no access token: {body}")
    return access


def run_dbt_step(step):
    return subprocess.run(
        ["docker", "exec", "-w", step["workdir"], step["container"],
         "bash", "-lc", step["command"]],
    ).returncode


def run_http_step(step, base_url, token):
    url = f"{base_url}{step['path']}"
    request = urllib.request.Request(
        url,
        data=step["body"].encode() if step["body"] else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=step["method"],
    )

    try:
        with urllib.request.urlopen(request, timeout=step.get("timeout", 3600)) as response:
            status, raw = response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        print(f"  HTTP {exc.code}: {exc.read().decode()[:400]}")
        return 1
    except urllib.error.URLError as exc:
        print(f"  could not reach {url}: {exc.reason}")
        return 1

    print(f"  HTTP {status}: {raw[:400]}")

    # These endpoints report failure as {"success": false, "error": ...} with a
    # 200 status, so a 2xx check alone would call a failed collect a success.
    # Orchestra's HTTP task only checks the status code - see the warning in
    # orchestra/README.md.
    try:
        payload = json.loads(raw)
    except ValueError:
        return 0
    if isinstance(payload, dict) and payload.get("success") is False:
        print(f"  reported success=false: {payload.get('error')}")
        return 1
    return 0


# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", "-p", type=Path, default=DEFAULT_PIPELINE,
                        help="pipeline YAML to run")
    parser.add_argument("--input", action="append", default=[], metavar="KEY=VAL",
                        help="override a pipeline input (repeatable)")
    parser.add_argument("--container", default="nba_app_backend",
                        help="container to exec dbt in")
    parser.add_argument("--project-root", default="/nba_app",
                        help="repo mount point inside the container")
    parser.add_argument("--base-url", default="http://localhost:8000",
                        help="base URL for HTTP tasks (Orchestra keeps this in the "
                             "connection, so it is not in the YAML)")
    parser.add_argument("--select", dest="only", metavar="ID",
                        help="run only this group or task id")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the resolved plan without executing")
    args = parser.parse_args()

    overrides = {}
    for item in args.input:
        if "=" not in item:
            parser.error(f"--input expects KEY=VAL, got '{item}'")
        key, value = item.split("=", 1)
        overrides[key] = value

    base_url = args.base_url.rstrip("/")

    try:
        spec = yaml.safe_load(args.path.read_text())
        inputs = resolve_inputs(spec.get("inputs"), overrides)
        plan = [
            (gid, tid, build_step(task, inputs, args.container, args.project_root))
            for gid, tid, task in collect_tasks(spec["pipeline"], only=args.only)
        ]
    except (PipelineError, KeyError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not plan:
        print(f"error: nothing to run (--select {args.only!r} matched no tasks)",
              file=sys.stderr)
        return 1

    print(f"pipeline: {spec.get('name')}  ({args.path.name})")
    print(f"inputs:   {inputs or '{}'}")

    # Only fetch a token if something actually needs one.
    token = None
    if any(step["kind"] == "http" for _, _, step in plan) and not args.dry_run:
        env = {**read_env_file(REPO_ROOT / ".env"), **os.environ}
        try:
            token = get_api_token(base_url, env)
        except PipelineError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"api:      {base_url} (authenticated)")
    print()

    started = time.time()
    for index, (group_id, task_id, step) in enumerate(plan, 1):
        if step["kind"] == "dbt":
            detail = f"$ {step['command']}  (in {step['workdir']})"
        else:
            detail = f"{step['method']} {base_url}{step['path']}"
        print(f"[{index}/{len(plan)}] {group_id}.{task_id}\n  {detail}")

        if args.dry_run:
            continue

        task_started = time.time()
        if step["kind"] == "dbt":
            code = run_dbt_step(step)
        else:
            code = run_http_step(step, base_url, token)
        elapsed = time.time() - task_started

        if code != 0:
            print(f"  FAILED in {elapsed:.1f}s (exit {code})\n")
            print(f"pipeline FAILED at {group_id}.{task_id}", file=sys.stderr)
            return code
        print(f"  SUCCEEDED in {elapsed:.1f}s\n")

    verb = "planned" if args.dry_run else "SUCCEEDED"
    print(f"pipeline {verb} - {len(plan)} task(s) in {time.time() - started:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
