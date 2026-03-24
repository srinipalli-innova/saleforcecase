from pydantic import BaseModel, Field
from typing import Optional


class SalesforceConfig(BaseModel):
    username: str
    password: str
    consumer_key: str
    consumer_secret: str
    user_secret_key: str = ""
    instance_url: str = "https://innovasolutionsat--agentforce.sandbox.my.salesforce.com"
    token_url: str = "https://innovasolutionsat--agentforce.sandbox.my.salesforce.com/services/oauth2/token"


class CaseRequest(BaseModel):
    subject: str
    description: Optional[str] = None
    status: str = "New"
    origin: str = "Web"
    priority: str = "Medium"
    type: Optional[str] = None
    owner_email: Optional[str] = None
    account_id: Optional[str] = Field(default=None, alias="AccountId")
    contact_id: Optional[str] = Field(default=None, alias="ContactId")

    def to_sf_payload(self) -> dict:
        """Convert to Salesforce API payload (PascalCase keys)."""
        payload = {
            "Subject": self.subject,
            "Status": self.status,
            "Origin": self.origin,
            "Priority": self.priority,
        }
        if self.description:
            payload["Description"] = self.description
        if self.type:
            payload["Type"] = self.type
        if self.account_id:
            payload["AccountId"] = self.account_id
        if self.contact_id:
            payload["ContactId"] = self.contact_id
        return payload


class CaseResponse(BaseModel):
    id: str
    success: bool
    errors: list = []
