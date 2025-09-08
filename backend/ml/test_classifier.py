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
        full_pipeline = model_data['pipeline']  # Load the pipeline
        class_names = model_data['class_names'] # Load class names
    except Exception as e:
        return {"error": f"Error loading the classifier model: {e}"}

    # Ensure new_data is a dictionary
    if not isinstance(new_data, dict):
        return {"error": "Input data must be a dictionary with feature names as keys."}

    # Get the feature names the model was trained on (excluding the target)
    feature_names_from_pipeline = full_pipeline.named_steps['preprocessor'].transformers_[0][2].tolist() + \
                                    list(full_pipeline.named_steps['preprocessor'].transformers_[1][2])

    # Ensure all expected features are present in the input data
    if set(feature_names_from_pipeline) != set(new_data.keys()):
        return {"error": "Missing or extraneous features in input data."}

    try:
        # Create DataFrame with correct column order
        new_data_df = pd.DataFrame([new_data])[feature_names_from_pipeline]

        # Make predictions
        predictions = full_pipeline.predict(new_data_df)
        predicted_classes = [class_names[i] for i in predictions] # Convert numerical predictions to original class names

        # Get probabilities (if available)
        probabilities = None
        if hasattr(full_pipeline, "predict_proba"):
            probabilities = full_pipeline.predict_proba(new_data_df).tolist()

        result = {
            "predictions": predicted_classes,
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