import os
import sys
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from zone_migration import ZoneRequest, migrate_payment_zone


def test_unapproved_payment_zone_is_held_without_a_write():
    client = Mock()
    result = migrate_payment_zone(client, ZoneRequest("pay.example.com", "gateway.example.net", False))
    assert result.notification == "held for risk review"
    client.domain_get.assert_not_called()
    client.record_upsert.assert_not_called()


def test_approved_payment_zone_uses_zone_id_for_the_record():
    client = Mock()
    client.domain_get.return_value = {"ok": True, "data": {"zone_id": "zone_42"}}
    result = migrate_payment_zone(client, ZoneRequest("pay.example.com", "gateway.example.net", True))
    assert result.zone_id == "zone_42"
    client.record_upsert.assert_called_once()
    assert client.record_upsert.call_args.args[0]["zone_id"] == "zone_42"


def test_pending_domain_is_added_before_writing_record():
    client = Mock()
    client.domain_get.return_value = {"ok": True, "data": {"state": "pending", "zone_id": ""}}
    client.domain_add.return_value = {"ok": True, "data": {"zone_id": "zone_42"}}
    result = migrate_payment_zone(client, ZoneRequest("pay.example.com", "gateway.example.net", True))
    assert result.zone_id == "zone_42"
    client.domain_add.assert_called_once_with("pay.example.com")
    client.record_upsert.assert_called_once()
