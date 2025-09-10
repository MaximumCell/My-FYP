

def recommend_model(df):
    """Suggest a good starting ML model based on simple dataset heuristics.

    Returns a single model name (string) for backward compatibility.
    Heuristics consider:
      - number of rows and columns
      - fraction of numeric vs categorical features
      - fraction of missing values
      - uniqueness / cardinality of columns (helps detect categorical targets)
      - approximate skewness of numeric features

    This is intentionally conservative: it recommends a robust, well-rounded
    model rather than trying to be optimal for every case.
    """
    # Basic shape
    try:
        num_rows, num_cols = df.shape
    except Exception:
        return "random_forest"

    if num_cols == 0:
        return "linear_regression"

    # Column type counts
    num_numeric = len(df.select_dtypes(include=["number"]).columns)
    num_categorical = len(df.select_dtypes(include=["object", "category"]).columns)

    # Missing values
    pct_missing = df.isna().mean().mean()

    # Average unique ratio (unique / n_rows) across columns
    try:
        unique_ratios = [df[col].nunique(dropna=True) / max(1, num_rows) for col in df.columns]
        avg_unique_ratio = sum(unique_ratios) / len(unique_ratios)
    except Exception:
        avg_unique_ratio = 1.0

    # Rough skewness indicator for numeric features (abs mean skew)
    try:
        skew_vals = df.select_dtypes(include=["number"]).skew().abs()
        mean_abs_skew = float(skew_vals.mean()) if not skew_vals.empty else 0.0
    except Exception:
        mean_abs_skew = 0.0

    # Heuristic: if many object/category cols or many low-cardinality columns, assume classification
    low_cardinality_cols = sum(1 for col in df.columns if df[col].nunique(dropna=True) <= max(10, int(0.05 * num_rows)))
    prefers_classification = False
    if num_categorical >= max(1, int(0.25 * num_cols)):
        prefers_classification = True
    if low_cardinality_cols >= max(1, int(0.1 * num_cols)):
        prefers_classification = True

    # If almost all columns are numeric and have high unique ratios, prefer regression
    prefers_regression = False
    if num_numeric >= max(1, int(0.75 * num_cols)) and avg_unique_ratio > 0.5:
        prefers_regression = True

    # Choose the model lists
    regression_candidates = [
        "linear_regression",
        "ridge_regression",
        "lasso_regression",
        "random_forest",
        "gradient_boosting",
        "svm",
        "knn",
    ]

    classification_candidates = [
        "logistic_regression",
        "random_forest",
        "gradient_boosting",
        "svm",
        "knn",
        "decision_tree",
        "naive_bayes",
    ]

    # Scoring function for regression candidates (simple rules)
    def score_regression(name):
        score = 0
        # Favor linear methods for small, low-dimensional, fairly clean numeric data
        if name == "linear_regression":
            if num_rows < 500 and num_cols <= 10 and pct_missing < 0.1 and mean_abs_skew < 1.0:
                score += 20
        if name == "ridge_regression" or name == "lasso_regression":
            if num_cols > 20 or num_cols > num_rows:
                score += 15
        if name == "random_forest":
            # good all-rounder, handles missing and categorical
            score += 10
            if pct_missing > 0.1 or num_categorical > 0:
                score += 10
            if num_rows > 5000:
                score += 10
        if name == "gradient_boosting":
            if 500 < num_rows <= 20000:
                score += 12
        if name == "svm":
            if num_rows < 2000 and num_cols < 50 and num_numeric >= num_cols:
                score += 8
        if name == "knn":
            if num_rows < 2000 and num_cols < 20:
                score += 6
        return score

    # Scoring for classification candidates
    def score_classification(name):
        score = 0
        if name == "logistic_regression":
            if num_rows >= 200 and num_numeric >= max(1, int(0.5 * num_cols)) and low_cardinality_cols == 0:
                score += 20
        if name == "random_forest":
            score += 12
            if pct_missing > 0.05 or num_categorical > 0:
                score += 8
            if num_rows > 5000:
                score += 8
        if name == "gradient_boosting":
            if 500 < num_rows <= 20000:
                score += 12
        if name == "svm":
            if num_rows < 2000 and num_numeric >= num_cols:
                score += 8
        if name == "knn":
            if num_rows < 2000 and num_cols < 30:
                score += 6
        if name == "naive_bayes":
            if num_categorical > 0 and num_rows < 5000:
                score += 10
        if name == "decision_tree":
            if num_rows < 1000:
                score += 6
        return score

    # Compute best candidate for each task
    best_reg = max(regression_candidates, key=score_regression)
    best_clf = max(classification_candidates, key=score_classification)

    # Final decision: pick based on preferences
    if prefers_classification and not prefers_regression:
        return best_clf
    if prefers_regression and not prefers_classification:
        return best_reg

    # If ambiguous, prefer robust tree-based models for mixed/dirty data
    if pct_missing > 0.1 or num_categorical > 0 or mean_abs_skew > 1.0:
        # prefer tree methods
        return "random_forest"

    # If large dataset choose tree/ensemble
    if num_rows > 10000:
        return "random_forest"

    # If medium dataset prefer gradient boosting
    if 1000 < num_rows <= 10000:
        return "gradient_boosting"

    # Fall back to chosen regression if most cols numeric, else classification candidate
    if num_numeric >= num_categorical:
        return best_reg
    return best_clf
