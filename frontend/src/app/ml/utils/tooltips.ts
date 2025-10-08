export const modelDescriptions: Record<string, string> = {
    'random_forest': 'Random Forest: ensemble of decision trees. Good default for tabular data, handles non-linearities, less sensitive to scaling.',
    'gradient_boosting': 'Gradient Boosting: powerful boosting ensemble. Often higher accuracy but slower to train. Tune learning_rate and n_estimators.',
    'logistic_regression': 'Logistic Regression: linear classifier for binary/multiclass (with multinomial). Works well on linearly separable data.',
    'svm': 'SVM: effective in high-dimensional spaces. Try RBF kernel for non-linear boundaries. Sensitive to feature scaling.',
    'knn': 'KNN: instance-based learner. Choose n_neighbors carefully; works better with fewer features.',
    'decision_tree': 'Decision Tree: interpretable tree model. Prune or set max_depth to avoid overfitting.',
    'mlp': 'MLP (Deep Learning): feed-forward neural network; good for complex patterns. Set epochs, batch_size and consider normalizing features.',
};

export const paramDescriptions: Record<string, string> = {
    'epochs': 'Number of passes over the entire training dataset. More epochs may improve performance but can overfit.',
    'batch_size': 'Number of samples per gradient update. Larger batch sizes use more memory but can speed up training.',
    'n_estimators': 'Number of trees in ensemble models (RandomForest/GradientBoosting). More can improve performance up to a point.',
    'max_depth': 'Maximum depth for tree-based models. Shallow depth reduces overfitting; deep trees may overfit.',
    'learning_rate': 'Step size shrinkage for boosting methods. Lower values may require more estimators.',
    'C': 'Inverse regularization strength for Logistic Regression; smaller values specify stronger regularization.',
    'kernel': 'SVM kernel type. "rbf" handles non-linear boundaries; try linear for large sparse data.',
    'n_neighbors': 'Number of neighbors to use for KNN classifier.',
};
