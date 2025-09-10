import os
import time
import io
import csv
from typing import Tuple, List, Optional

PLOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'plots')


def ensure_plots_dir():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    return PLOTS_DIR


def unique_path(prefix: str, ext: str) -> str:
    ensure_plots_dir()
    ts = int(time.time() * 1000)
    filename = f"{prefix}_{ts}.{ext.lstrip('.')}"
    return os.path.join(PLOTS_DIR, filename)


def read_csv_file(file_storage) -> Tuple[List[str], List[List[float]]]:
    """Return header and rows (as floats where possible).

    file_storage may be a Flask FileStorage or a file-like object.
    """
    stream = file_storage.stream if hasattr(file_storage, 'stream') else io.StringIO(file_storage.read().decode('utf-8'))
    reader = csv.reader(stream)
    rows = list(reader)
    if not rows:
        return [], []
    header = rows[0]
    data = []
    for r in rows[1:]:
        parsed = []
        for v in r:
            try:
                parsed.append(float(v))
            except Exception:
                parsed.append(v)
        data.append(parsed)
    return header, data
