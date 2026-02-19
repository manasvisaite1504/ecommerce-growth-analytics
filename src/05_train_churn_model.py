from duckdb import df
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    confusion_matrix, classification_report
)

DATA_PATH = "data/processed/churn_repeat_purchase_dataset.csv"

def main():
    df = pd.read_csv(DATA_PATH)

    feature_cols = [
        "recency_days",
        "frequency",
        "monetary",
        "avg_order_value",
        "customer_lifetime_days",
    ]

    y = df["label_repeat_60d"]
    X = df[feature_cols]


    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train_scaled, y_train)

    proba = model.predict_proba(X_test_scaled)[:, 1]
    pred = (proba >= 0.5).astype(int)

    roc = roc_auc_score(y_test, proba)
    ap = average_precision_score(y_test, proba)
    f1 = f1_score(y_test, pred)
    cm = confusion_matrix(y_test, pred)

    print("\n=== Repeat Purchase within 60 Days (Logistic Regression) ===")
    print(f"ROC-AUC: {roc:.4f}")
    print(f"PR-AUC:  {ap:.4f}")
    print(f"F1:      {f1:.4f}")
    print("\nConfusion Matrix:\n", cm)
    print("\nClassification Report:\n", classification_report(y_test, pred))

    coef_df = pd.DataFrame({"feature": feature_cols, "coef": model.coef_[0]})
    coef_df = coef_df.sort_values("coef", ascending=False)

    print("\nTop positive drivers (increase repeat probability):")
    print(coef_df.head(10).to_string(index=False))

    print("\nTop negative drivers (decrease repeat probability):")
    print(coef_df.tail(10).to_string(index=False))

if __name__ == "__main__":
    main()
