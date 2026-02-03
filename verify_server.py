import time
import urllib.request
import json
import sys
import subprocess
import os

BASE_URL = "http://localhost:3000"

def test_get_evaluate():
    print("Testing GET /evaluate...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/evaluate") as response:
            if response.status != 200:
                print(f"FAILED: Expected 200, got {response.status}")
                return False
            content = response.read().decode('utf-8')
            if "<!DOCTYPE html>" not in content and "<html" not in content:
                 print("FAILED: Response does not look like HTML")
                 return False
            print("PASSED")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_post_evaluate_valid():
    print("Testing POST /evaluate (valid)...")
    data = {
        "user": {
            "id": "user-123",
            "level": 12,
            "country": "Turkey",
            "first_session": 1672531200,
            "last_session": 1735689600,
            "purchase_amount": 15000,
            "last_purchase_at": 1735600000
        },
        "segments": {
            "high_level": "level > 10"
        }
    }
    req = urllib.request.Request(
        f"{BASE_URL}/evaluate",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"FAILED: Expected 200, got {response.status}")
                return False
            result = json.loads(response.read().decode('utf-8'))
            if "results" not in result:
                print(f"FAILED: 'results' missing in response: {result}")
                return False
            if result["results"].get("high_level") is not True:
                print(f"FAILED: Expected high_level=True, got {result['results'].get('high_level')}")
                return False
            print("PASSED")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_post_evaluate_invalid():
    print("Testing POST /evaluate (invalid types)...")
    # Invalid level type "high"
    data = {
        "user": {
            "id": "user-123",
            "level": "high", 
            "country": "Turkey",
            "first_session": 1672531200,
            "last_session": 1735689600,
            "purchase_amount": 15000,
            "last_purchase_at": 1735600000
        },
        "segments": {}
    }
    req = urllib.request.Request(
        f"{BASE_URL}/evaluate",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(req)
        print("FAILED: Expected 400, got 200/Success")
        return False
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("PASSED: Got 400 Bad Request as expected")
            return True
        else:
            print(f"FAILED: Expected 400, got {e.code}")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_post_evaluate_now():
    print("Testing POST /evaluate (_now)...")
    # last_session is 1735689600 (Jan 1 2025)
    # Current time (simulated or real) is > 2025.
    data = {
        "user": {
            "id": "user-123",
            "level": 12,
            "country": "Turkey",
            "first_session": 1672531200,
            "last_session": 1735689600,
            "purchase_amount": 15000,
            "last_purchase_at": 1735600000
        },
        "segments": {
            "is_past": "last_session < _now()",
            "is_future": "last_session > _now()"
        }
    }
    req = urllib.request.Request(
        f"{BASE_URL}/evaluate",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"FAILED: Expected 200, got {response.status}")
                return False
            result = json.loads(response.read().decode('utf-8'))
            if result["results"].get("is_past") is not True:
                print(f"FAILED: Expected is_past=True")
                return False
            if result["results"].get("is_future") is not False:
                print(f"FAILED: Expected is_future=False")
                return False
            print("PASSED")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_post_evaluate_sql_syntax():
    print("Testing POST /evaluate (SQL syntax: =, AND/OR)...")
    data = {
        "user": {
            "id": "u4",
            "level": 20,
            "country": "Turkey",
            "first_session": 1600000000,
            "last_session": 1700000000,
            "purchase_amount": 25000,
            "last_purchase_at": 1700000000
        },
        "segments": {
            "tr_eq": "country = 'Turkey'",
            "tr_and_level": "country = 'Turkey' AND level >= 10",
            "or_clause": "level > 100 OR purchase_amount > 20000"
        }
    }
    req = urllib.request.Request(
        f"{BASE_URL}/evaluate",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"FAILED: Expected 200, got {response.status}")
                return False
            result = json.loads(response.read().decode('utf-8'))
            if result["results"].get("tr_eq") is not True:
                print(f"FAILED: tr_eq (country = 'Turkey') expected True")
                return False
            if result["results"].get("tr_and_level") is not True:
                print(f"FAILED: tr_and_level expected True")
                return False
            if result["results"].get("or_clause") is not True:
                print(f"FAILED: or_clause expected True")
                return False
            print("PASSED")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    # Ensure server is running (checking port)
    # We assume the server is started externally for this script
    
    # Wait a bit for server to be ready if we just started it
    time.sleep(2)

    tests = [
        test_get_evaluate,
        test_post_evaluate_valid,
        test_post_evaluate_invalid,
        test_post_evaluate_now,
        test_post_evaluate_sql_syntax
    ]
    
    failed = False
    for test in tests:
        if not test():
            failed = True
    
    if failed:
        sys.exit(1)
    sys.exit(0)
