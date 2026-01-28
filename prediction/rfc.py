import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
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

    # Cross-validation before hyperparameter tuning
    print("\n## Model Training and Evaluation")
    print("------------------------------------------------")
    print("Step 1: Cross-validation with default parameters...")
    base_rfc = RandomForestClassifier(n_estimators=100, random_state=42)
    cv_scores = cross_val_score(base_rfc, X_train, y_train, cv=5, scoring='accuracy')
    print(f"  5-Fold CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"  Individual fold scores: {[f'{s:.4f}' for s in cv_scores]}")

    # Hyperparameter tuning
    print("\nStep 2: Hyperparameter tuning with GridSearchCV...")
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    grid_search = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=5,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)

    print(f"\n  Best parameters found: {grid_search.best_params_}")
    print(f"  Best CV accuracy: {grid_search.best_score_:.4f}")

    # Use the best model
    rfc = grid_search.best_estimator_

    # Evaluate on test set
    print("\nStep 3: Final evaluation on test set...")
    y_pred = rfc.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)

    print("\n## Model Results (Random Forest Classifier)")
    print("------------------------------------------------")
    print(f"Test Set Accuracy: {accuracy:.4f}")
    print(f"Training Set Accuracy: {rfc.score(X_train, y_train):.4f}")
    print("\n### Classification Report:")
    print(report)

    importances = rfc.feature_importances_
    feature_series = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    
    os.makedirs(save_path, exist_ok=True)
    importance_filepath = os.path.join(save_path, 'feature_importances.csv')
    feature_series.to_csv(importance_filepath, header=['Importance'])

    importance_txt_filepath = os.path.join(save_path, 'feature_importances.txt')
    with open(importance_txt_filepath, 'w') as f:
        f.write(feature_series.to_string())

    # Full Feature Importances
    print("\n### Full Feature Importances (All Features):")
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

    print(f"\nModel saved successfully to: {model_filepath}")
    print(f"LabelEncoder saved successfully to: {encoder_filepath}")
    print(f"Feature Importances saved to text file: {importance_txt_filepath}")
    print(f"Feature Importance Plot saved to: {plot_filepath}")

    return rfc, le
