from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

from models import SalesforceConfig, CaseRequest, CaseResponse
from sf_client import SalesforceClient

app = FastAPI(title="Salesforce Case API", version="1.0.0")


def load_properties(filepath: str) -> dict:
    props = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                props[key.strip()] = value.strip()
    return props


def get_sf_client() -> SalesforceClient:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    props = load_properties(os.path.join(base_dir, "config.properties"))
    config = SalesforceConfig(
        username=props["SF_USERNAME"],
        password=props["SF_PASSWORD"],
        consumer_key=props["SF_CONSUMER_KEY"],
        consumer_secret=props["SF_CONSUMER_SECRET"],
        user_secret_key=props.get("SF_USER_SECRET_KEY", ""),
    )
    client = SalesforceClient(config)
    client.authenticate()
    return client, props


class CreateCaseRequest(BaseModel):
    subject: str
    description: Optional[str] = None
    status: str = "New"
    origin: str = "Web"
    priority: str = "Medium"
    type: Optional[str] = None
    account_id: Optional[str] = None
    contact_id: Optional[str] = None


class CreateCaseResponse(BaseModel):
    case_id: str
    success: bool
    errors: list = []


@app.post("/cases", response_model=CreateCaseResponse, summary="Create a Salesforce Case")
def create_case(request: CreateCaseRequest):
    try:
        client, props = get_sf_client()

        case = CaseRequest(
            subject=request.subject,
            description=request.description,
            status=request.status,
            origin=request.origin,
            priority=request.priority,
            type=request.type,
            owner_email=props.get("SF_CASE_OWNER"),
            AccountId=request.account_id,
            ContactId=request.contact_id,
        )

        result = client.create_case(case)
        return CreateCaseResponse(
            case_id=result.id,
            success=result.success,
            errors=result.errors,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
