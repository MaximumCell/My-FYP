export function suggestHyperparamsForModel({ selectedModel, rows, nFeatures }: { selectedModel: string; rows: number; nFeatures: number }) {
    const suggestions: Record<string, string | number> = {};
    if (!selectedModel) {
        return suggestions;
    }
    const m = selectedModel.toLowerCase();
    if (m.includes('random_forest')) {
        suggestions.n_estimators = rows < 200 ? 100 : 200;
        suggestions.max_depth = nFeatures < 10 ? 10 : 20;
        suggestions.n_jobs = -1;
    } else if (m.includes('gradient_boosting')) {
        suggestions.n_estimators = 100;
        suggestions.learning_rate = 0.1;
        suggestions.max_depth = 3;
    } else if (m.includes('logistic')) {
        suggestions.C = 1.0;
        suggestions.solver = rows < 500 ? 'liblinear' : 'saga';
        suggestions.max_iter = 200;
    } else if (m.includes('svm')) {
        suggestions.C = 1.0;
        suggestions.kernel = 'rbf';
    } else if (m.includes('knn')) {
        suggestions.n_neighbors = Math.max(3, Math.round(Math.sqrt(Math.max(rows, 9))));
    } else if (m.includes('decision_tree')) {
        suggestions.max_depth = nFeatures < 10 ? 10 : 20;
    } else if (m.includes('lasso')) {
        suggestions.alpha = 0.01;
        suggestions.max_iter = 2000;
    } else if (m.includes('ridge')) {
        suggestions.alpha = 1.0;
    } else {
        suggestions.random_state = 42;
    }
    return suggestions;
}
