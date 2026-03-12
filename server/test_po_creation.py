import requests
import json
import sys

def test():
    try:
        # Login first 
        print("Attempting login...")
        login = requests.post('http://localhost:8000/api/v1/auth/login', json={ 
            'email': 'payalshinde906@gmail.com', 
            'password': 'Admin@123',
            'gstin': '22AAAAD0000A1Z5'
        }) 
        print(f'Login status: {login.status_code}') 
        
        if login.status_code != 200:
            print(f"Login failed: {login.text}")
            return

        login_data = login.json()
        token = login_data.get('data', {}).get('access_token') or login_data.get('access_token')
        if not token:
            token = login.cookies.get('access_token')
        
        print(f'Token: {token[:20]}...' if token else 'Token: NOT FOUND') 

        if not token:
            print('Login failed, no token found in response or cookies.')
            return

        # Create PO 
        print("Attempting PO creation...")
        po = requests.post('http://localhost:8000/api/v1/pos', 
            headers={'Authorization': f'Bearer {token}'}, 
            json={ 
                'po_number': 'PO-TEST-001', 
                'vendor': 'Ollama Test Vendor', 
                'gstin': '22AAAAD0000A1Z5', 
                'amount': 5000, 
                'due_date': '2026-04-01', 
                'status': 'open', 
                'vendor_email': 'test@test.com', 
                'vendor_phone': '+919999999999' 
            } 
        ) 
        print(f'PO creation status: {po.status_code}') 
        print('PO response:', json.dumps(po.json(), indent=2)) 
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test()
