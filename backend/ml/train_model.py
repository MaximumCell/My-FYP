import pandas as pd
import joblib
import os
from flask import jsonify

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

# Available models with default parameters
models = {
    "linear_regression": LinearRegression,
    "ridge_regression": Ridge,
    "lasso_regression": Lasso,
    "random_forest": RandomForestRegressor,
    "gradient_boosting": GradientBoostingRegressor,
    "svm": SVR,
    "knn": KNeighborsRegressor
}

# Available scalers
scalers = {
    "standard": StandardScaler,
    "minmax": MinMaxScaler
}

def train_model(file, model_name, target_column=None, test_size=0.2, hyperparams={}, scaling_method="standard"):
    """Trains a machine learning model with preprocessing and pipeline."""
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        return {"error": f"File not found at {file}"}
    except Exception as e:
        return {"error": f"Error reading CSV file: {e}"}

    if target_column is None:
        if df.shape[1] == 0:
            return {"error": "Dataset is empty or has no columns."}
        target_column = df.columns[-1]

    if target_column not in df.columns:
        return {"error": f"Target column '{target_column}' not found in dataset"}

    X = df.drop(columns=[target_column])
    y = df[target_column]

    numerical_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns

    numeric_transformer_steps = [('imputer', SimpleImputer(strategy='mean'))]

    if scaling_method in scalers:
        numeric_transformer_steps.append(('scaler', scalers[scaling_method]()))
    else:
        print(f"Warning: Invalid scaling method '{scaling_method}'. No scaling applied.")

    numeric_transformer = Pipeline(steps=numeric_transformer_steps)

    categorical_transformer_steps = [('imputer', SimpleImputer(strategy='most_frequent'))]
    categorical_transformer_steps.append(('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
    categorical_transformer = Pipeline(steps=categorical_transformer_steps)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough'
    )

    if model_name not in models:
        return {"error": f"Invalid model name: {model_name}"}

    model_class = models[model_name]
    model_instance = model_class(**hyperparams)

    full_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                     ('regressor', model_instance)])

    if not (0 < test_size < 1):
        return {"error": "Test size should be between 0 and 1"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    full_pipeline.fit(X_train, y_train)

    y_pred = full_pipeline.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    model_dir = "trained_models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{model_name}_pipeline.pkl")

    # Try to get feature names after preprocessing (sklearn >=1.0 supports get_feature_names_out)
    feature_names = X.columns.tolist()
    feature_names_out = None
    try:
        # Attempt to get feature names out from the preprocessor
        feature_names_out = preprocessor.get_feature_names_out(feature_names)
    except Exception:
        # fallback: try to build a reasonable feature list
        try:
            # If transformers_ exists, attempt to collect transformer output names
            fn_out = []
            for name, transformer, cols in preprocessor.transformers_:
                if name == 'remainder' and preprocessor.remainder == 'passthrough':
                    continue
                # cols may be an Index or list
                if hasattr(cols, 'tolist'):
                    cols_list = cols.tolist()
                else:
                    cols_list = list(cols) if cols is not None else []
                # For onehot encoding, we can't know categories here reliably; append original col names
                fn_out.extend(cols_list)
            if fn_out:
                feature_names_out = fn_out
        except Exception:
            feature_names_out = None

    try:
        joblib.dump({
            'pipeline': full_pipeline,
            'feature_names': feature_names,
            'feature_names_out': list(feature_names_out) if feature_names_out is not None else None,
            'target_column': target_column,
            'config': {
                'test_size': test_size,
                'scaling_method': scaling_method,
                'hyperparams': hyperparams
            }
        }, model_path)
    except Exception as e:
        return {"error": f"Error saving the trained pipeline: {e}"}

    return {
        "message": "Model trained successfully",
        "model_path": model_path,
        "mean_squared_error": mse,
        "mean_absolute_error": mae,
        "r2_score": r2
    }

def test_model(model_name, new_data):
    """Load a trained model and make predictions on new input data."""
    model_path = f"trained_models/{model_name}_pipeline.pkl"

    if not os.path.exists(model_path):
        return {"error": "Model not found"}
    # Load saved model data (may contain pipeline and metadata)
    try:
        model_data = joblib.load(model_path)
    except Exception as e:
        return {"error": f"Error loading model: {e}"}

    # Support older saved pipelines where only the pipeline object was saved
    if isinstance(model_data, dict):
        full_pipeline = model_data.get('pipeline')
        feature_names_out = model_data.get('feature_names_out')
        feature_names = model_data.get('feature_names')
    else:
        full_pipeline = model_data
        feature_names_out = None
        feature_names = None

    if full_pipeline is None:
        return {"error": "Invalid model file: pipeline not found."}

    # Determine expected features.
    # Prefer the original feature names captured during training (feature_names) because
    # the pipeline's preprocessor may produce transformed output names like 'num__col' or 'cat__col_A'.
    # Users will typically provide raw feature names (original), so validate against those first.
    if feature_names:
        expected_features = list(feature_names)
    elif feature_names_out:
        # If only feature_names_out is available, check if the incoming data already uses those
        # transformed names; otherwise fall back to using the keys provided by the user.
        try:
            if any(fn in new_data.keys() for fn in feature_names_out):
                expected_features = list(feature_names_out)
            else:
                expected_features = list(new_data.keys())
        except Exception:
            expected_features = list(new_data.keys())
    else:
        # As a last resort, try to derive from the preprocessor (may fail for older sklearn)
        try:
            preprocessor = full_pipeline.named_steps.get('preprocessor')
            if preprocessor is not None and hasattr(preprocessor, 'get_feature_names_out'):
                # Need original input column names; try to use new_data keys as columns
                expected_features = list(preprocessor.get_feature_names_out(list(new_data.keys())))
            else:
                expected_features = list(new_data.keys())
        except Exception:
            expected_features = list(new_data.keys())

    # Validate input keys
    input_keys = list(new_data.keys())
    missing = [f for f in expected_features if f not in input_keys]
    extra = [k for k in input_keys if k not in expected_features]
    if missing or extra:
        msg_parts = []
        if missing:
            msg_parts.append(f"missing: {missing}")
        if extra:
            msg_parts.append(f"extra: {extra}")
        return {"error": f"Feature mismatch. {', '.join(msg_parts)}"}

    try:
        new_data_df = pd.DataFrame([new_data])[expected_features]
        predictions = full_pipeline.predict(new_data_df)
        return {"predictions": predictions.tolist()}
    except Exception as e:
        return {"error": f"Error during prediction: {e}"}