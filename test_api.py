import requests

BASE_URL = "http://localhost:8000"


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.json()}")


def test_create_case_minimal():
    payload = {
        "subject": "Minimal Test Case"
    }
    response = requests.post(f"{BASE_URL}/cases", json=payload)
    print(f"Minimal Case: {response.json()}")


def test_create_case_full():
    payload = {
        "subject": "Full Test Case from Python",
        "description": "This case was created via the SFDC API test script.",
        "status": "New",
        "origin": "Web",
        "priority": "High",
        "type": "Question"
    }
    response = requests.post(f"{BASE_URL}/cases", json=payload)
    result = response.json()
    print(f"Full Case Response: {result}")
    if response.status_code == 200:
        print(f"  Case ID  : {result['case_id']}")
        print(f"  Success  : {result['success']}")
    else:
        print(f"  Error: {result['detail']}")


if __name__ == "__main__":
    print("=== Testing Salesforce Case API ===\n")
    test_health()
    print()
    test_create_case_minimal()
    print()
    test_create_case_full()
