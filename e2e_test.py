import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "payalshinde906@gmail.com"
ADMIN_PASS = "AdminPass123!"
ADMIN_GSTIN = "22AAAAD0000A1Z5"

def test_e2e():
    print("🚀 Starting End-to-End Test...")
    
    # 1. Test Login
    print("\n1. Testing Login...")
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASS,
        "gstin": ADMIN_GSTIN
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        if res.status_code == 200:
            token = res.json()["data"]["access_token"]
            print("✅ Login Successful")
        else:
            print(f"❌ Login Failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Create PO (with Audit Log)
    print("\n2. Testing Create PO...")
    po_payload = {
        "po_number": f"TEST-PO-{int(time.time())}",
        "vendor": "Test Vendor",
        "gstin": "27AAACR1234A1Z1",
        "amount": 5000,
        "due_date": "2026-05-01",
        "status": "Open",
        "reason": "E2E Testing Create"
    }
    try:
        res = requests.post(f"{BASE_URL}/purchase-orders", json=po_payload, headers=headers, timeout=30)
        if res.status_code == 200:
            po_id = res.json()["data"]["id"]
            print(f"✅ PO Created: {po_id}")
        else:
            print(f"❌ PO Create Failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ PO Create Error: {e}")
        return

    # 3. Test Audit Logs (Search for the creation)
    print("\n3. Testing Audit Logs Search...")
    try:
        params = {"search": po_payload["po_number"]}
        res = requests.get(f"{BASE_URL}/audit-logs", params=params, headers=headers, timeout=10)
        if res.status_code == 200:
            logs = res.json()["data"]
            if len(logs) > 0 and logs[0]["action"] == "CREATE":
                print("✅ Audit Log found for creation")
            else:
                print(f"❌ Audit Log not found or incorrect: {logs}")
        else:
            print(f"❌ Audit Logs Failed: {res.text}")
    except Exception as e:
        print(f"❌ Audit Logs Error: {e}")

    # 4. Test Chatbot
    print("\n4. Testing Chatbot...")
    try:
        chat_payload = {"message": "Hello, are you working?"}
        res = requests.post(f"{BASE_URL}/chat", json=chat_payload, headers=headers, timeout=65)
        if res.status_code == 200:
            print(f"✅ Chatbot Responded: {res.json()['data']['reply'][:50]}...")
        else:
            print(f"❌ Chatbot Failed: {res.text}")
    except Exception as e:
        print(f"❌ Chatbot Error: {e}")

    # 5. Cleanup - Delete PO
    print("\n5. Testing Delete PO (with Reason)...")
    try:
        delete_payload = {"reason": "E2E Testing Cleanup"}
        res = requests.delete(f"{BASE_URL}/purchase-orders/{po_id}", json=delete_payload, headers=headers, timeout=10)
        if res.status_code == 200:
            print("✅ PO Deleted Successfully")
        else:
            print(f"❌ PO Delete Failed: {res.text}")
    except Exception as e:
        print(f"❌ PO Delete Error: {e}")

    print("\n🏁 E2E Test Completed!")

if __name__ == "__main__":
    test_e2e()
