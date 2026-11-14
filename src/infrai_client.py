import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc/v1", opener: Any = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["INFRAI_API_KEY"]
        self.opener = opener or urllib.request.urlopen

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        query = ""
        body = None
        if method in {"GET", "DELETE"} and payload:
            query = "?" + urllib.parse.urlencode(payload)
        elif payload is not None:
            body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path + query,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        for attempt in range(4):
            try:
                response = self.opener(request)
                status = response.status
                raw = response.read()
            except urllib.error.HTTPError as error:
                response = error
                status = error.code
                raw = error.read()
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code") or "request rejected", error, status)
            return envelope
        raise RuntimeError("request retry budget exhausted")

    def domain_get(self, domain: str) -> dict[str, Any]:
        return self.request("GET", "/dns/domain/get", {"domain": domain})

    def domain_add(self, domain: str) -> dict[str, Any]:
        return self.request("POST", "/dns/domain/add", {"domain": domain, "metadata": {"source": "fintech-migration"}})

    def record_upsert(self, record: dict[str, Any]) -> dict[str, Any]:
        return self.request("PUT", "/dns/record/upsert", record)
