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
    # Ensure ext is not None and handle it properly
    if ext is None:
        ext = 'png'  # default extension
    ext = str(ext).lstrip('.')
    filename = f"{prefix}_{ts}.{ext}"
    return os.path.join(PLOTS_DIR, filename)


def read_csv_file(file_storage) -> Tuple[List[str], List[List[float]]]:
    """Return header and rows (as floats where possible).

    file_storage may be a Flask FileStorage or a file-like object.
    """
    # Get a file-like stream. Flask's FileStorage provides a binary stream
    # (bytes). csv.reader expects text (str) lines, so wrap binary streams
    # with a TextIOWrapper to provide a text interface.
    if hasattr(file_storage, 'stream'):
        stream = file_storage.stream
        # If the stream is binary (no 'encoding' attr), wrap it
        if not getattr(stream, 'encoding', None):
            stream = io.TextIOWrapper(stream, encoding='utf-8')
            # ensure we start from the beginning
            try:
                stream.seek(0)
            except Exception:
                pass
    else:
        # file_storage may be raw bytes content
        stream = io.StringIO(file_storage.read().decode('utf-8'))

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
