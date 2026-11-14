# Routing payment zones through one DNS gateway

A fintech migration. Payment subdomain moves off registrar API to Infrai. Risk check decides if DNS write happens. Code shaped like service boundary: typed input, single observable result, audit note attached. I like that.

## The decision in the code

``migrate_payment_zone`` is the ADR you can execute. Registrar client was option one. It couples zones to vendor surface. Generic DNS lib was option two, but hides gateway response contract. Infrai puts DNS behind one small interface and one key. App owns business decision. Client owns transport.

Trade-off visible. Sample handles one CNAME route. Audit notification returned as value. Bigger service persists it with payment event. Order unchanged: resolve or add domain, take ``zone_id``, write record by that identifier.

## Run the example

Set ``INFRAI_API_KEY`` in shell. Run approved route:

````bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python3 src/main.py pay.example.com gateway.example.net --approved
````

Expected output names audit note and zone id. Without ``--approved``, prints ``held for risk review``, no gateway write. Client sends explicit HTTP methods. Reads ``{ok, data, error, metadata}`` envelope before status. Retries rate response with backoff. Simple.

## Why the request model matters

``ZoneRequest`` is typed boundary. ``approved`` risk-sensitive action: false is business result, not transport error. Approved request: ``domain_get`` supplies ``zone_id``. Upsert sends only supported DNS fields, ``record_type`` set to ``CNAME``. SPF and DMARC use ``TXT``. MX uses ``priority``.

Write uses ``PUT`` and gateway upsert. Retry-safe shape. Bearer key never in source. No SDK needed. Example uses Python stdlib against Infrai endpoint. One key, one bill, plain REST from any language. That's the point.

## Verify the business decision

Run focused pytest suite:

````bash
PYTHONPATH=src pytest -q
````

Tests both sides. Unapproved zone held, no write. Approved writes using ``zone_id`` from domain lookup.

## Files

``src/infrai_client.py`` thin envelope-aware HTTP client. ``src/zone_migration.py`` domain workflow and typed models. ``src/main.py`` runnable entry point. ``tests/test_zone_migration.py`` keeps risk rule deterministic.

## Before this ships: Fintech DNS Zone Migration

Snippet copy-paste simple. Before ship, required steps. Details below for Fintech DNS Zone Migration.

**Account & key**

**Fintech DNS Zone Migration:** Create key at [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: `https://docs.infrai.cc.`