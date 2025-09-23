import pandas as pd
import joblib
from flask import jsonify
import os

def test_classifier(model_name, new_data):
    """Load a trained classification model and make predictions on new input data."""
    model_path = f"trained_classifiers/{model_name}_classifier_pipeline.pkl"

    if not os.path.exists(model_path):
        return {"error": "Classifier model not found"}

    try:
        model_data = joblib.load(model_path)
        if isinstance(model_data, dict):
            full_pipeline = model_data.get('pipeline')
            class_names = model_data.get('class_names')
            feature_names_out = model_data.get('feature_names_out')
            feature_names = model_data.get('feature_names')
        else:
            full_pipeline = model_data
            class_names = None
            feature_names_out = None
            feature_names = None
    except Exception as e:
        return {"error": f"Error loading the classifier model: {e}"}

    # Ensure new_data is a dictionary
    if not isinstance(new_data, dict):
        return {"error": "Input data must be a dictionary with feature names as keys."}

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
        # fallback: try to derive from preprocessor if possible, otherwise use incoming keys
        try:
            preprocessor = full_pipeline.named_steps.get('preprocessor')
            if preprocessor is not None and hasattr(preprocessor, 'get_feature_names_out'):
                # attempt to derive using incoming new_data keys as base
                expected_features = list(preprocessor.get_feature_names_out(list(new_data.keys())))
            else:
                expected_features = list(new_data.keys())
        except Exception:
            expected_features = list(new_data.keys())

    # Validate input keys
    missing = [f for f in expected_features if f not in new_data.keys()]
    extra = [k for k in new_data.keys() if k not in expected_features]
    if missing or extra:
        msg = ''
        if missing:
            msg += f"missing: {missing}. "
        if extra:
            msg += f"extra: {extra}."
        return {"error": f"Feature mismatch. {msg}"}

    try:
        new_data_df = pd.DataFrame([new_data])[expected_features]
        predictions = full_pipeline.predict(new_data_df)
        predicted_classes = None
        if class_names is not None:
            predicted_classes = [class_names[i] for i in predictions]

        probabilities = None
        # If pipeline has predict_proba method at top-level
        try:
            if hasattr(full_pipeline, 'predict_proba'):
                probabilities = full_pipeline.predict_proba(new_data_df).tolist()
        except Exception:
            probabilities = None

        result = {
            "predictions": predicted_classes if predicted_classes is not None else predictions.tolist(),
            "probabilities": probabilities,
            "class_names": class_names
        }
        return result
    except Exception as e:
        return {"error": f"Error during prediction: {e}"}

if __name__ == '__main__':
    # Example Usage (for testing the function directly)
    # Create a dummy trained model file (you'd normally get this from training)
    # For simplicity, we'll create a very basic model and save it.
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    import numpy as np

    # Dummy data for demonstration
    X_train = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': ['A', 'B', 'A', 'C', 'B']
    })
    y_train = np.array([0, 1, 0, 2, 1])
    class_names = ['negative', 'positive', 'neutral']

    # Create a simple pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),  # Add scaling
        ('classifier', LogisticRegression())
    ])
    pipeline.fit(X_train, y_train)

    # Save the pipeline and class names
    joblib.dump({
        'pipeline': pipeline,
        'class_names': class_names
    }, 'trained_classifiers/dummy_classifier_classifier_pipeline.pkl')

    # Dummy test data (matching the features used in training)
    test_data = {
        'feature1': 3,
        'feature2': 'B'
    }

    result = test_classifier('dummy_classifier', test_data)
    print(result)

    os.remove('trained_classifiers/dummy_classifier_classifier_pipeline.pkl') # clean up