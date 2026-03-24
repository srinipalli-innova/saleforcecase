import requests
from models import SalesforceConfig, CaseRequest, CaseResponse


class SalesforceClient:
    def __init__(self, config: SalesforceConfig):
        self.config = config
        self.access_token: str | None = None
        self.instance_url: str = config.instance_url

    def authenticate(self) -> None:
        """Authenticate using OAuth2 Username-Password flow."""
        payload = {
            "grant_type": "password",
            "client_id": self.config.consumer_key,
            "client_secret": self.config.consumer_secret,
            "username": self.config.username,
            "password": self.config.password + self.config.user_secret_key,
        }
        response = requests.post(self.config.token_url, data=payload)
        if not response.ok:
            print(f"Auth failed [{response.status_code}]: {response.text}")
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.instance_url = token_data.get("instance_url", self.config.instance_url)
        # Extract current user ID from the identity URL (last segment)
        identity_url = token_data.get("id", "")
        self.current_user_id = identity_url.rstrip("/").split("/")[-1]
        print(f"Authenticated successfully. Instance URL: {self.instance_url}")
        print(f"Identity URL from token: {identity_url}")
        print(f"Parsed User ID: {self.current_user_id}")

    def _headers(self) -> dict:
        if not self.access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_user_id_by_username(self, username: str) -> str:
        """Look up a Salesforce User ID by username."""
        query = f"SELECT Id, Name FROM User WHERE Username = '{username}' LIMIT 1"
        url = f"{self.instance_url}/services/data/v59.0/query"
        response = requests.get(url, headers=self._headers(), params={"q": query})
        response.raise_for_status()
        records = response.json().get("records", [])
        if not records:
            raise ValueError(f"No Salesforce user found with username: {username}")
        user = records[0]
        print(f"Case Owner resolved: {user['Name']} ({user['Id']})")
        return user["Id"]

    def create_case(self, case: CaseRequest) -> CaseResponse:
        """Create a Case in Salesforce and return the response."""
        url = f"{self.instance_url}/services/data/v59.0/sobjects/Case"
        payload = case.to_sf_payload()

        if case.owner_email:
            owner_id = self.get_user_id_by_username(self.config.username)
            payload["OwnerId"] = owner_id

        headers = self._headers()
        headers["Sforce-Auto-Assign"] = "FALSE"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        return CaseResponse(
            id=data["id"],
            success=data["success"],
            errors=data.get("errors", []),
        )
