"""Probe optional service credentials without printing secrets or mutating state."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import sys
from typing import Any
from urllib import error, request


DEFAULT_TIMEOUT = 30


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="print failures but return 0 so the report can be inspected interactively",
    )
    args = parser.parse_args()

    env = load_env_file(Path(args.env_file))
    results = [
        probe_firecrawl(env, args.timeout),
        probe_github(env, args.timeout),
        probe_cloudflare(env, args.timeout),
        probe_cloudflare_r2(env, args.timeout),
        probe_clickhouse_cloud(env, args.timeout),
        probe_stripe(env, args.timeout),
    ]
    for result in results:
        print(render_result(result))

    failed_results = [item for item in results if item["status"] == "fail"]
    return 0 if args.no_fail or not failed_results else 1


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def probe_firecrawl(env: dict[str, str], timeout: int) -> dict[str, str]:
    key = env.get("FIRECRAWL_API_KEY")
    if not key:
        return skipped("firecrawl", "missing FIRECRAWL_API_KEY")
    response = get_json(
        "https://api.firecrawl.dev/v2/team/activity?limit=1",
        {"Authorization": f"Bearer {key}"},
        timeout,
    )
    if not response["ok"]:
        return failed("firecrawl", response)
    payload = response["payload"]
    data = payload.get("data") if isinstance(payload, dict) else None
    count = len(data) if isinstance(data, list) else "unknown"
    return passed("firecrawl", f"team activity readable, items={count}")


def probe_github(env: dict[str, str], timeout: int) -> dict[str, str]:
    key = env.get("GITHUB_TOKEN")
    if not key:
        return skipped("github", "missing GITHUB_TOKEN")
    response = get_json(
        "https://api.github.com/user",
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {key}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout,
    )
    if not response["ok"]:
        return failed("github", response)
    payload = response["payload"]
    login = payload.get("login", "unknown") if isinstance(payload, dict) else "unknown"
    remaining = response["headers"].get("X-RateLimit-Remaining", "unknown")
    return passed("github", f"authenticated as {login}, rate_remaining={remaining}")


def probe_cloudflare(env: dict[str, str], timeout: int) -> dict[str, str]:
    token = env.get("CLOUDFLARE_API_TOKEN")
    if not token:
        return skipped("cloudflare", "missing CLOUDFLARE_API_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    verify = get_json("https://api.cloudflare.com/client/v4/user/tokens/verify", headers, timeout)
    account_id = env.get("CLOUDFLARE_ACCOUNT_ID")
    if verify["ok"] and not account_id:
        return passed("cloudflare", "token verified, missing CLOUDFLARE_ACCOUNT_ID")
    if account_id:
        account = get_json(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}",
            headers,
            timeout,
        )
        if account["ok"]:
            if verify["ok"]:
                return passed("cloudflare", "user token verified and account readable")
            return passed(
                "cloudflare",
                "account readable, user-token verify rejected this token type",
            )
        if verify["ok"]:
            return failed("cloudflare", account)
    return failed("cloudflare", verify)


def probe_cloudflare_r2(env: dict[str, str], timeout: int) -> dict[str, str]:
    account_id = env.get("CLOUDFLARE_ACCOUNT_ID")
    token = env.get("CLOUDFLARE_R2_API_TOKEN") or env.get("CLOUDFLARE_API_TOKEN")
    if not account_id or not token:
        return skipped("cloudflare_r2", "missing CLOUDFLARE_ACCOUNT_ID or R2 token")
    response = get_json(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets",
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout,
    )
    if not response["ok"]:
        detail = summarize_error(response["payload"])
        if "10042" in detail or "enable R2" in detail:
            return {
                "detail": "account token works, but R2 is not enabled or not entitled on this account",
                "service": "cloudflare_r2",
                "status": "fail",
            }
        return failed("cloudflare_r2", response)
    payload = response["payload"]
    result = payload.get("result") if isinstance(payload, dict) else None
    buckets = result.get("buckets") if isinstance(result, dict) else result
    count = len(buckets) if isinstance(buckets, list) else "unknown"
    return passed("cloudflare_r2", f"R2 buckets readable, count={count}")


def probe_clickhouse_cloud(env: dict[str, str], timeout: int) -> dict[str, str]:
    key_id = env.get("CLICKHOUSE_CLOUD_KEY_ID") or env.get("CLICKHOUSE_KEY_ID")
    key_secret = env.get("CLICKHOUSE_CLOUD_KEY_SECRET") or env.get("CLICKHOUSE_KEY_SECRET")
    if not key_id or not key_secret:
        return skipped(
            "clickhouse_cloud",
            "missing CLICKHOUSE_CLOUD_KEY_ID and CLICKHOUSE_CLOUD_KEY_SECRET",
        )
    response = get_json(
        "https://api.clickhouse.cloud/v1/organizations",
        basic_auth(key_id, key_secret),
        timeout,
    )
    if not response["ok"]:
        return failed("clickhouse_cloud", response)
    payload = response["payload"]
    result = payload.get("result") if isinstance(payload, dict) else None
    count = len(result) if isinstance(result, list) else "unknown"
    return passed("clickhouse_cloud", f"organizations readable, count={count}")


def probe_stripe(env: dict[str, str], timeout: int) -> dict[str, str]:
    key = env.get("STRIPE_SECRET_KEY")
    if not key:
        return skipped("stripe", "missing STRIPE_SECRET_KEY")
    response = get_json("https://api.stripe.com/v1/account", basic_auth(key, ""), timeout)
    if not response["ok"]:
        return failed("stripe", response)
    payload = response["payload"]
    if not isinstance(payload, dict):
        return passed("stripe", "account readable")
    mode = "live" if key.startswith("sk_live_") else "test" if key.startswith("sk_test_") else "unknown"
    return passed(
        "stripe",
        "account readable, "
        f"key_mode={mode}, charges_enabled={payload.get('charges_enabled')}, "
        f"payouts_enabled={payload.get('payouts_enabled')}",
    )


def get_json(url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read(1024 * 512)
            return {
                "headers": dict(response.headers),
                "ok": 200 <= response.status < 300,
                "payload": parse_json(raw),
                "status_code": response.status,
            }
    except error.HTTPError as exc:
        raw = exc.read(1024 * 256)
        return {
            "headers": dict(exc.headers),
            "ok": False,
            "payload": parse_json(raw),
            "status_code": exc.code,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "headers": {},
            "ok": False,
            "payload": {"error": type(exc).__name__, "message": str(exc)},
            "status_code": "error",
        }


def parse_json(raw: bytes) -> Any:
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {"body_prefix": raw.decode("utf-8", errors="replace")[:300]}


def basic_auth(user: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def passed(service: str, detail: str) -> dict[str, str]:
    return {"detail": detail, "service": service, "status": "pass"}


def skipped(service: str, detail: str) -> dict[str, str]:
    return {"detail": detail, "service": service, "status": "skip"}


def failed(service: str, response: dict[str, Any]) -> dict[str, str]:
    return {
        "detail": f"http={response['status_code']} {summarize_error(response['payload'])}",
        "service": service,
        "status": "fail",
    }


def summarize_error(payload: Any) -> str:
    if not isinstance(payload, dict):
        return str(payload)[:240]
    for key in ("error", "message", "errors", "type"):
        value = payload.get(key)
        if value:
            return str(value)[:240]
    return str(payload)[:240]


def render_result(result: dict[str, str]) -> str:
    label = {"fail": "FAIL", "pass": "PASS", "skip": "SKIP"}[result["status"]]
    return f"{label} {result['service']}: {result['detail']}"


if __name__ == "__main__":
    sys.exit(main())
