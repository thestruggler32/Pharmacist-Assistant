import requests
import json

BASE = 'http://localhost:5000'
results = []

def log(msg):
    print(msg)
    results.append(msg)

def test_login(email, role_name):
    log(f'\n=== Test: {role_name} Login ===')
    try:
        res = requests.post(f'{BASE}/api/login', json={'email': email, 'password': 'password'}, timeout=5)
        log(f'Status: {res.status_code}')
        if res.ok:
            data = res.json()
            token = data.get('token')
            user = data.get('user', {})
            log(f'SUCCESS - Role: {user.get("role")}, Name: {user.get("name")}')
            return token
        else:
            log(f'FAILED: {res.text[:200]}')
            return None
    except Exception as e:
        log(f'ERROR: {str(e)}')
        return None

def test_prescriptions(token, role):
    log(f'\n=== Test: List Prescriptions ({role}) ===')
    try:
        res = requests.get(f'{BASE}/api/prescriptions', headers={'Authorization': f'Bearer {token}'}, timeout=5)
        log(f'Status: {res.status_code}')
        if res.ok:
            data = res.json()
            count = len(data.get('prescriptions', []))
            log(f'SUCCESS - Found {count} prescriptions')
            return True
        else:
            log(f'FAILED: {res.text[:200]}')
            return False
    except Exception as e:
        log(f'ERROR: {str(e)}')
        return False

def test_alternatives(token):
    log(f'\n=== Test: Alternatives Endpoint ===')
    try:
        res = requests.post(f'{BASE}/api/medicines/alternatives', 
            json={'medicine_name': 'Paracetamol'},
            headers={'Authorization': f'Bearer {token}'}, timeout=5)
        log(f'Status: {res.status_code}')
        if res.ok:
            data = res.json()
            alts = data.get('alternatives', [])
            log(f'SUCCESS - Found {len(alts)} alternatives')
            log(f'User Region: {data.get("user_region")}')
            log(f'Locality: {data.get("locality")}')
            return True
        else:
            log(f'FAILED: {res.text[:200]}')
            return False
    except Exception as e:
        log(f'ERROR: {str(e)}')
        return False

if __name__ == '__main__':
    log('='*50)
    log('PHARMACIST ASSISTANT - API TESTS')
    log('='*50)
    
    # Test all logins
    patient_token = test_login('patient1@test.com', 'Patient 1')
    patient2_token = test_login('patient2@test.com', 'Patient 2')
    doctor_token = test_login('doctor@test.com', 'Doctor')
    pharmacist_token = test_login('pharmacist@test.com', 'Pharmacist')
    
    # Test prescriptions listing
    if patient_token:
        test_prescriptions(patient_token, 'Patient')
    if pharmacist_token:
        test_prescriptions(pharmacist_token, 'Pharmacist')
    
    # Test alternatives
    if pharmacist_token:
        test_alternatives(pharmacist_token)
    
    log('\n' + '='*50)
    log('ALL TESTS COMPLETE')
    log('='*50)
    
    # Write to file
    with open('backend/test_results.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))
    print('\nResults written to backend/test_results.txt')
