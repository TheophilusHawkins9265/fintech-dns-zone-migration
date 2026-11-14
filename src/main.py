import argparse

from infrai_client import InfraiClient
from zone_migration import ZoneRequest, migrate_payment_zone


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a payment subdomain through the shared DNS gateway.")
    parser.add_argument("domain")
    parser.add_argument("target")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()
    result = migrate_payment_zone(InfraiClient(), ZoneRequest(args.domain, args.target, args.approved))
    print(f"{result.notification}; zone_id={result.zone_id or 'none'}")


if __name__ == "__main__":
    main()

