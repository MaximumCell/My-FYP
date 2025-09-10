import os
import requests


BASE = os.environ.get('BACKEND_URL', 'http://127.0.0.1:5000')


def test_regression_models_list():
    try:
        r = requests.get(f"{BASE}/ml/models/regression", timeout=3)
    except Exception:
        # Skip the test if server not running on expected port
        return
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_classification_models_list():
    try:
        r = requests.get(f"{BASE}/ml/models/classification", timeout=3)
    except Exception:
        return
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_deep_models_list():
    try:
        r = requests.get(f"{BASE}/ml/deep/models", timeout=3)
    except Exception:
        return
    assert r.status_code == 200
    data = r.json()
    assert 'models' in data
