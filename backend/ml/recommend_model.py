

def recommend_model(df):
    """Automatically suggest a model based on dataset properties."""
    num_rows, num_cols = df.shape

    if num_rows < 1000:
        if num_cols < 10:
            return "linear_regression"
        else:
            return "ridge_regression"
    elif num_rows > 10000:
        return "random_forest"
    else:
        return "gradient_boosting"
