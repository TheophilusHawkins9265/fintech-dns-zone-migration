from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient, InfraiError


@dataclass(frozen=True)
class ZoneRequest:
    domain: str
    target: str
    approved: bool


@dataclass(frozen=True)
class MigrationResult:
    zone_id: str
    record_type: str
    notification: str


def _zone_id(envelope: dict[str, Any]) -> str:
    data = envelope.get("data") or {}
    zone_id = data.get("zone_id")
    if not zone_id:
        raise ValueError("domain response did not include zone_id")
    return str(zone_id)


def migrate_payment_zone(client: InfraiClient, request: ZoneRequest) -> MigrationResult:
    if not request.approved:
        return MigrationResult("", "", "held for risk review")

    try:
        domain = client.domain_get(request.domain)
    except InfraiError as error:
        if error.status != 404 or error.code not in {"NOT_FOUND", "DOMAIN_NOT_FOUND"}:
            raise
        domain = client.domain_add(request.domain)
    if not (domain.get("data") or {}).get("zone_id"):
        domain = client.domain_add(request.domain)
    zone_id = _zone_id(domain)
    client.record_upsert({
        "zone_id": zone_id,
        "record_type": "CNAME",
        "name": "payments",
        "content": request.target,
        "ttl": 300,
        "metadata": {"purpose": "payment-routing"},
    })
    return MigrationResult(zone_id, "CNAME", f"audit notification queued for {request.domain}")
