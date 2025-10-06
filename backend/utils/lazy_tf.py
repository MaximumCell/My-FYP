"""Lazy TensorFlow proxy

This module provides a proxy object `tf` which imports the real
`tensorflow` package on first attribute access. Use `from backend.utils.lazy_tf import tf`
or `from utils.lazy_tf import tf` depending on import paths.

This avoids importing TensorFlow at module-import time and lets the
application lazy-load TF only when needed (helpful on low-memory hosts).
"""

_tf = None

class _TFProxy:
    def __getattr__(self, name):
        global _tf
        if _tf is None:
            try:
                import tensorflow as tf
                _tf = tf
            except Exception as e:
                # Re-raise ImportError for callers to handle
                raise ImportError(f"TensorFlow not available: {e}")
        return getattr(_tf, name)

    def __repr__(self):
        return f"<Lazy TensorFlow proxy (loaded={_tf is not None})>"


def is_available() -> bool:
    """Return True if TensorFlow can be imported without raising."""
    global _tf
    if _tf is not None:
        return True
    try:
        import importlib
        importlib.import_module('tensorflow')
        return True
    except Exception:
        return False


tf = _TFProxy()
