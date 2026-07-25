from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

STRATEGY_REGISTRY = {
    "logistic_regression": lambda: LogisticRegression(max_iter=1000),
    "random_forest": lambda: RandomForestClassifier(n_estimators=300, max_depth=5, min_samples_leaf=20, random_state=42)
}