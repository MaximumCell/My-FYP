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

    try:
        joblib.dump(full_pipeline, model_path)
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

    full_pipeline = joblib.load(model_path)
    preprocessor = full_pipeline.named_steps['preprocessor']

    print("Preprocessor transformers:")
    feature_names_from_pipeline = []
    for name, transformer, columns in preprocessor.transformers_:
        print(f"  Name: {name}, Columns: {columns}")
        if not columns.empty:
            feature_names_from_pipeline.extend(columns.tolist())
        elif name == 'remainder' and preprocessor.remainder == 'passthrough':
            # If you had passthrough columns, you'd need to know their names here
            # For example, if you stored them during training:
            # feature_names_from_pipeline.extend(passthrough_column_names)
            pass

    print(f"Expected feature names from pipeline: {feature_names_from_pipeline}")
    print(f"Received test data keys: {new_data.keys()}")

    if set(feature_names_from_pipeline) != set(new_data.keys()):
        return {"error": "Missing or extra features in input data."}

    try:
        new_data_df = pd.DataFrame([new_data])[feature_names_from_pipeline]
        print("Shape of test DataFrame before prediction:", new_data_df.shape)
        predictions = full_pipeline.predict(new_data_df)
        print("Predictions shape:", predictions.shape)
        return {"predictions": predictions.tolist()}
    except Exception as e:
        print(f"Error during prediction: {e}")
        return {"error": f"Error during prediction: {e}"}