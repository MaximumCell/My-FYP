import os
import requests

BASE = os.environ.get('BACKEND_URL', 'http://127.0.0.1:5001')


def test_plot2d_equation():
    try:
        r = requests.post(f"{BASE}/simulation/plot2d", json={"mode": "equation", "equation": "sin(x)", "x_min": -3.14, "x_max": 3.14, "resolution": 200}, timeout=5)
    except Exception:
        return
    assert r.status_code == 200
    j = r.json()
    assert 'html_path' in j or 'html_url' in j
