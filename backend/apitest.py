import requests
import json

# Base URL of the FastAPI server
base_url = "http://127.0.0.1:8000"  # Modify if necessary


# Test the /api/v1/questions endpoint
def test_ask_question():
    url = f"{base_url}/api/v1/questions"
    data = {
        "session_id": 21,
        "previous_questions": ["121"],
        "current_question": "What are the rules for thesis submission?"
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


# Test the /api/v1/feedback endpoint
def test_feedback():
    url = f"{base_url}/api/v1/feedback"
    data = {
        "question_id": 1,
        "rating": 5,
        "comments": "The answer was very helpful."
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


# Test the /api/v1/policies/upload endpoint
def test_upload_policy():
    url = f"{base_url}/api/v1/policies/upload"
    response = requests.post(url)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


# Test the /api/v1/policies endpoint
def test_get_policies():
    url = f"{base_url}/api/v1/policies"
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


if __name__ == "__main__":
    print("Testing /api/v1/questions endpoint...")
    test_ask_question()

    print("\nTesting /api/v1/feedback endpoint...")
    test_feedback()

    print("\nTesting /api/v1/policies/upload endpoint...")
    test_upload_policy()

    print("\nTesting /api/v1/policies endpoint...")
    test_get_policies()
