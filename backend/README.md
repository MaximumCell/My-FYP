# Backend ML Endpoints

This README documents the ML-related endpoints in the backend and how to run smoke tests.

Base URL: http://127.0.0.1:5000 (or 5001 if you start the server on that port)

Endpoints

- GET /ml/models/regression -> list available regression model names
- POST /ml/train/regression -> multipart form: file (CSV), model (name), target_column (optional)
- POST /ml/test/regression -> JSON: {"model": "<name>", "new_data": {..}}
- GET /ml/models/classification -> list classification models
- POST /ml/train/classification -> multipart form: file (CSV), model (name), target_column
- POST /ml/test/classification -> JSON: {"model": "<name>", "new_data": {..}}
- POST /ml/get_columns -> multipart form: file (CSV)
- POST /ml/recommend -> multipart form: file (CSV)

Deep learning endpoints (experimental)

- GET /ml/deep/models -> lists supported deep model templates
- POST /ml/deep/train -> multipart form: file (CSV), model (mlp|cnn|sequence|transformer), epochs, batch_size, target_column
- POST /ml/deep/test -> JSON: {"model": "mlp", "model_path": "<model_path>", "input": {...}}

Running smoke tests

1. Start the backend (recommended to use the project venv):

```bash
source backend/venv/bin/activate
python backend/app.py
```

2. From the repo root run pytest in the backend folder:

```bash
cd backend
pip install pytest requests
pytest -q
```

Notes

- Deep training scripts are placeholders with simple loaders. For production use, replace image/sequence loaders with robust TF Datasets pipelines and move heavy training to background jobs (RQ/Celery).
- TensorFlow may require a specific Python version (3.11 recommended) if you encounter wheel issues.
