import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

def train_and_save_rfc(df: pd.DataFrame, save_path: str):
    """
    Trains a Random Forest Classifier (RFC) for cafe prediction and saves 
    the trained model and LabelEncoder to the specified path.

    Args:
        df: The pandas DataFrame containing the features and target.
        save_path: The directory path where the model and encoder should be saved.
    
    Returns:
        tuple: (trained rfc model, fitted LabelEncoder)
    """

    target_variable = 'name_updated'
    feature_variables = [
        'parks_count_1km',
        'open_bars_count_500m', 'lst_celsius_1km', 'temp_max', 'temp_min',
        'precip_mm', 'ndvi', 'nightlight'
    ]

    df[target_variable] = df[target_variable].str.strip()
    X = df[feature_variables].copy()

    le = LabelEncoder()
    y = le.fit_transform(df[target_variable])

    final_features = X.columns.tolist()

    print(f"Total unique classes (cafés) found: {len(le.classes_)}")
    print(f"Total features used: {len(final_features)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    rfc = RandomForestClassifier(n_estimators=100, random_state=42)
    rfc.fit(X_train, y_train)

    y_pred = rfc.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)

    print("\n## 📊 Model Results (Random Forest Classifier) 📊")
    print("------------------------------------------------")
    print(f"Overall Accuracy: {accuracy:.2f}\n")
    print("### Classification Report:")
    print(report)

    importances = rfc.feature_importances_
    feature_series = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    
    os.makedirs(save_path, exist_ok=True)
    importance_filepath = os.path.join(save_path, 'feature_importances.csv')
    feature_series.to_csv(importance_filepath, header=['Importance'])

    importance_txt_filepath = os.path.join(save_path, 'feature_importances.txt')
    with open(importance_txt_filepath, 'w') as f:
        f.write(feature_series.to_string())

    # --- 👇 NEW: Full Feature Importances Printed Cleanly ---
    print("\n### 📈 Full Feature Importances (All Features):")
    for feature, score in feature_series.items():
        print(f"    - {feature:<25}: {score:.6f}")
    print("------------------------------------------------")

    # --- Smaller plot (8x5) ---
    plt.figure(figsize=(8, 5))
    feature_series.plot(kind='barh')
    plt.title('Feature Importance for Cafe Classification')
    plt.xlabel('Feature Importance Score')
    plt.gca().invert_yaxis()
    
    plot_filepath = os.path.join(save_path, 'feature_importance_plot.png')
    plt.tight_layout()
    plt.savefig(plot_filepath)
    plt.show()
    plt.close()

    model_filepath = os.path.join(save_path, 'rfc_model.joblib')
    encoder_filepath = os.path.join(save_path, 'label_encoder.joblib')

    joblib.dump(rfc, model_filepath)
    joblib.dump(le, encoder_filepath)

    print(f"\n✅ Model saved successfully to: {model_filepath}")
    print(f"✅ LabelEncoder saved successfully to: {encoder_filepath}")
    print(f"✅ Feature Importances saved to text file: {importance_txt_filepath}")
    print(f"✅ Feature Importance Plot saved to: {plot_filepath}")

    return rfc, le
