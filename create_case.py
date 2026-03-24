"""
Entry point: Create a Salesforce Case via REST API.

Usage:
    python create_case.py

Credentials are read from config.properties in the same directory.
"""
import os
from models import SalesforceConfig, CaseRequest
from sf_client import SalesforceClient


def load_properties(filepath: str) -> dict:
    props = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                props[key.strip()] = value.strip()
    return props


def main():
    # ── Load credentials from config.properties ───────────────────────────────
    base_dir = os.path.dirname(os.path.abspath(__file__))
    props = load_properties(os.path.join(base_dir, "config.properties"))

    config = SalesforceConfig(
        username=props["SF_USERNAME"],
        password=props["SF_PASSWORD"],
        consumer_key=props["SF_CONSUMER_KEY"],
        consumer_secret=props["SF_CONSUMER_SECRET"],
        user_secret_key=props.get("SF_USER_SECRET_KEY", ""),
    )

    # ── Case payload ──────────────────────────────────────────────────────────
    case = CaseRequest(
        subject="Test Case from Python API",
        description="This case was created via the Salesforce REST API using Python.",
        status="New",
        origin="Web",
        priority="Medium",
        type="Question",
        owner_email=props.get("SF_CASE_OWNER"),
        # account_id="001XXXXXXXXXXXXXXX",  # optional
        # contact_id="003XXXXXXXXXXXXXXX",  # optional
    )

    # ── Authenticate & create ─────────────────────────────────────────────────
    client = SalesforceClient(config)
    client.authenticate()

    result = client.create_case(case)
    print(f"Case created successfully!")
    print(f"  Case ID : {result.id}")
    print(f"  Success  : {result.success}")
    if result.errors:
        print(f"  Errors   : {result.errors}")


if __name__ == "__main__":
    main()
