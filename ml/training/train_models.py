"""
IntelliGrievance AI - Model Training and Evaluation Pipeline
Trains and rigorously compares 4 ML architectures:
  1. Multinomial Naive Bayes
  2. Logistic Regression
  3. Linear Support Vector Machine (LinearSVC with CalibratedClassifierCV)
  4. Random Forest Classifier

Evaluates: Accuracy, Precision, Recall, Macro F1, Weighted F1, Confusion Matrices.
Selects the best performing model based on Macro F1 on held-out test split (80/20 stratified).
Serializes best models and saves full evaluation reports (JSON + CSV).
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.preprocessing.text_cleaner import clean_text

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "grievances_dataset.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def train_and_evaluate():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    # Preprocess text
    df["cleaned_text"] = df["text"].apply(lambda t: clean_text(str(t), remove_stopwords=False))
    
    X = np.array(df["cleaned_text"].tolist(), dtype=object)
    y_cat = np.array(df["category"].tolist(), dtype=object)
    y_pri = np.array(df["priority"].tolist(), dtype=object)
    
    # Stratified 80/20 train/test split
    X_train, X_test, y_cat_train, y_cat_test, y_pri_train, y_pri_test = train_test_split(
        X, y_cat, y_pri, test_size=0.2, random_state=42, stratify=y_cat
    )
    
    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_features=12000
    )
    
    # ── Category Classification Models Comparison ──────────────────────────
    models_to_test = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(C=5.0, max_iter=2000, random_state=42),
        "Linear Support Vector Machine": CalibratedClassifierCV(LinearSVC(C=1.0, random_state=42, dual=False)),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=35, random_state=42, n_jobs=-1)
    }
    
    comparison_results = []
    trained_pipelines = {}
    
    print("\n" + "="*70)
    print("CATEGORICAL CLASSIFICATION MODEL COMPARISON")
    print("="*70)
    
    for name, clf in models_to_test.items():
        pipe = Pipeline([
            ("tfidf", vectorizer),
            ("clf", clf)
        ])
        
        print(f"Training: {name}...")
        pipe.fit(X_train, y_cat_train)
        y_pred = pipe.predict(X_test)
        
        acc = accuracy_score(y_cat_test, y_pred)
        prec_macro = precision_score(y_cat_test, y_pred, average="macro", zero_division=0)
        rec_macro = recall_score(y_cat_test, y_pred, average="macro", zero_division=0)
        f1_macro = f1_score(y_cat_test, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_cat_test, y_pred, average="weighted", zero_division=0)
        
        print(f"  Accuracy:    {acc*100:.2f}%")
        print(f"  Macro F1:    {f1_macro:.4f}")
        print(f"  Weighted F1: {f1_weighted:.4f}")
        
        comparison_results.append({
            "model_name": name,
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4)
        })
        trained_pipelines[name] = pipe

    # Rank and select best category model
    comparison_results = sorted(comparison_results, key=lambda x: -x["f1_macro"])
    best_cat_model_name = comparison_results[0]["model_name"]
    best_cat_pipeline = trained_pipelines[best_cat_model_name]
    print(f"\n=> Best Category Model: {best_cat_model_name} (Macro F1 = {comparison_results[0]['f1_macro']:.4f})")
    
    # Detailed report for best category model
    y_cat_pred = best_cat_pipeline.predict(X_test)
    cat_report_dict = classification_report(y_cat_test, y_cat_pred, output_dict=True)
    cat_labels = sorted(list(set(y_cat_test)))
    cat_cm = confusion_matrix(y_cat_test, y_cat_pred, labels=cat_labels).tolist()
    
    # ── Priority Prediction Model Training ─────────────────────────────────
    print("\n" + "="*70)
    print("TRAINING PRIORITY / SEVERITY PREDICTOR")
    print("="*70)
    
    pri_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2, max_features=10000)),
        ("clf", LogisticRegression(C=6.0, max_iter=2000, random_state=42, class_weight="balanced"))
    ])
    
    pri_pipeline.fit(X_train, y_pri_train)
    y_pri_pred = pri_pipeline.predict(X_test)
    
    pri_acc = accuracy_score(y_pri_test, y_pri_pred)
    pri_f1_macro = f1_score(y_pri_test, y_pri_pred, average="macro", zero_division=0)
    pri_f1_weighted = f1_score(y_pri_test, y_pri_pred, average="weighted", zero_division=0)
    
    print(f"Priority Model Accuracy:    {pri_acc*100:.2f}%")
    print(f"Priority Model Macro F1:    {pri_f1_macro:.4f}")
    print(f"Priority Model Weighted F1: {pri_f1_weighted:.4f}")
    
    pri_report_dict = classification_report(y_pri_test, y_pri_pred, output_dict=True)
    pri_labels = ["Critical", "High", "Medium", "Low"]
    pri_cm = confusion_matrix(y_pri_test, y_pri_pred, labels=pri_labels).tolist()
    
    # ── Serialization ──────────────────────────────────────────────────────
    cat_model_file = os.path.join(MODELS_DIR, "best_category_pipeline.joblib")
    pri_model_file = os.path.join(MODELS_DIR, "severity_pipeline.joblib")
    
    joblib.dump(best_cat_pipeline, cat_model_file)
    joblib.dump(pri_pipeline, pri_model_file)
    print(f"\nSerialized Best Category Model: {os.path.abspath(cat_model_file)}")
    print(f"Serialized Severity Model:      {os.path.abspath(pri_model_file)}")
    
    # ── Save Evaluation Reports ────────────────────────────────────────────
    eval_summary = {
        "timestamp": datetime.now().isoformat(),
        "dataset": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "categories_count": len(cat_labels),
            "priorities_count": len(pri_labels)
        },
        "category_model_comparison": comparison_results,
        "selected_category_model": {
            "model_name": best_cat_model_name,
            "accuracy": comparison_results[0]["accuracy"],
            "f1_macro": comparison_results[0]["f1_macro"],
            "classification_report": cat_report_dict,
            "labels": cat_labels,
            "confusion_matrix": cat_cm
        },
        "severity_model": {
            "model_name": "Calibrated Logistic Regression (Class-Weighted)",
            "accuracy": round(float(pri_acc), 4),
            "f1_macro": round(float(pri_f1_macro), 4),
            "f1_weighted": round(float(pri_f1_weighted), 4),
            "classification_report": pri_report_dict,
            "labels": pri_labels,
            "confusion_matrix": pri_cm
        }
    }
    
    report_json_path = os.path.join(REPORTS_DIR, "model_evaluation_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)
        
    comp_df = pd.DataFrame(comparison_results)
    comp_df.to_csv(os.path.join(REPORTS_DIR, "model_comparison.csv"), index=False)
    print(f"Evaluation report written to: {os.path.abspath(report_json_path)}")
    
    return eval_summary

if __name__ == "__main__":
    train_and_evaluate()
