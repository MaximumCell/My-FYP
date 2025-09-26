import pandas as pd
import joblib
import os
from flask import jsonify

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score, classification_report, confusion_matrix, roc_auc_score, roc_auc_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB

# Available classification models with default parameters
classification_models = {
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "svm": SVC,
    "knn": KNeighborsClassifier,
    "decision_tree": DecisionTreeClassifier,
    "naive_bayes": GaussianNB
}

# Available scalers (same as for regression)
scalers = {
    "standard": StandardScaler,
    "minmax": MinMaxScaler
}

def train_classifier(file, model_name, target_column=None, test_size=0.2, hyperparams={}, scaling_method="standard"):
    """Trains a machine learning classifier with preprocessing and pipeline."""
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

    # Encode the target variable
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    class_names = label_encoder.classes_.tolist() # Store original class names

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

    if model_name not in classification_models:
        return {"error": f"Invalid classification model name: {model_name}"}

    model_class = classification_models[model_name]
    model_instance = model_class(**hyperparams)

    full_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                     ('classifier', model_instance)])

    if not (0 < test_size < 1):
        return {"error": "Test size should be between 0 and 1"}

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=test_size, random_state=42)

    full_pipeline.fit(X_train, y_train)

    y_pred = full_pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    # Get detailed classification report
    class_report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    
    # Get class distribution from training and test sets
    y_train_counts = pd.Series(y_train).value_counts().to_dict()
    y_test_counts = pd.Series(y_test).value_counts().to_dict()
    
    # Convert indices to class names for better readability
    train_class_distribution = {class_names[idx]: count for idx, count in y_train_counts.items() if idx < len(class_names)}
    test_class_distribution = {class_names[idx]: count for idx, count in y_test_counts.items() if idx < len(class_names)}

    # Handle binary and multi-class ROC AUC
    roc_auc = None
    if len(class_names) > 2:
        try:
            y_prob = full_pipeline.predict_proba(X_test)
            roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
        except Exception as e:
            print(f"Warning: Error calculating ROC AUC for multi-class: {e}")
    elif len(class_names) == 2:
        try:
            y_prob = full_pipeline.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_prob)
        except Exception as e:
            print(f"Warning: Error calculating ROC AUC for binary class: {e}")

    model_dir = "trained_classifiers"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{model_name}_classifier_pipeline.pkl")

    # Capture input feature names
    feature_names = X.columns.tolist()

    try:
        # Attempt to capture transformed feature names
        feature_names_out = None
        try:
            feature_names_out = preprocessor.get_feature_names_out(feature_names)
        except Exception:
            try:
                fn_out = []
                for name, transformer, cols in preprocessor.transformers_:
                    if name == 'remainder' and preprocessor.remainder == 'passthrough':
                        continue
                    if hasattr(cols, 'tolist'):
                        cols_list = cols.tolist()
                    else:
                        cols_list = list(cols) if cols is not None else []
                    fn_out.extend(cols_list)
                if fn_out:
                    feature_names_out = fn_out
            except Exception:
                feature_names_out = None

        joblib.dump({
            'pipeline': full_pipeline,
            'class_names': class_names,
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
        return {"error": f"Error saving the trained classifier pipeline: {e}"}

    return {
        "message": "Classifier trained successfully",
        "model_path": model_path,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm.tolist(),
        "roc_auc": roc_auc,
        "class_names": class_names,
        "classification_report": class_report,
        "train_class_distribution": train_class_distribution,
        "test_class_distribution": test_class_distribution,
        "n_train_samples": len(y_train),
        "n_test_samples": len(y_test),
        "n_features": len(feature_names) if feature_names else X_train.shape[1]
    }

def get_classifier_models():
    """Returns a list of available classification model names."""
    return list(classification_models.keys())

if __name__ == '__main__':
    # Example usage (for testing the function directly)
    # Create a dummy CSV file for testing
    data = {
        'feature1': [1, 2, 3, 4, 5],
        'feature2': ['A', 'B', 'A', 'C', 'B'],
        'target': ['positive', 'negative', 'positive', 'neutral', 'negative']
    }
    df = pd.DataFrame(data)
    df.to_csv('dummy_classification.csv', index=False)

    result = train_classifier('dummy_classification.csv', 'random_forest', target_column='target')
    print(result)

    os.remove('dummy_classification.csv') # Clean up dummy file