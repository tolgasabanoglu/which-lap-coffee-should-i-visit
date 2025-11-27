# --- dynamic_lookup.py ---
import numpy as np
import pandas as pd

def setup_feature_ranges(feature_ranges):
    """
    Extracts general min/max and percentile values from the feature_ranges table.
    """
    F_MIN = feature_ranges['Min']
    F_MAX = feature_ranges['Max']
    F_P25 = feature_ranges['25th Percentile (Low)']
    F_P50 = feature_ranges['50th Percentile (Mid)']
    F_P75 = feature_ranges['75th Percentile (High)']
    
    return F_MIN, F_P25, F_P50, F_P75, F_MAX


def setup_cafe_lookup(df):
    """
    Creates a cafe name/address lookup table and determines the friendly name column.
    """
    FRIENDLY_NAME_COL = None
    for col in ['name', 'datenamelatlon', 'date_name', 'name_updated']:
        if col in df.columns:
            FRIENDLY_NAME_COL = col
            break

    if not FRIENDLY_NAME_COL:
        FRIENDLY_NAME_COL = 'name_updated'
        print(f"\n⚠️ WARNING: Could not find a friendly name column. Falling back to 'name_updated'.")
    elif FRIENDLY_NAME_COL != 'name_updated':
        print(f"\nℹ️ INFO: Using column '{FRIENDLY_NAME_COL}' for friendly cafe names.")

    # Create lookup table
    cafe_lookup_df = df[['name_updated', FRIENDLY_NAME_COL, 'address']].drop_duplicates(subset=['name_updated'])
    cafe_lookup_df['name_updated'] = cafe_lookup_df['name_updated'].astype(str)
    cafe_lookup_df = cafe_lookup_df.set_index('name_updated')
    
    return cafe_lookup_df, FRIENDLY_NAME_COL


def setup_class_mapping(df, rfc):
    """
    Creates a mapping between model class labels and cafe names with failsafe for integer classes.
    """
    true_class_names = sorted(df['name_updated'].unique().tolist())
    class_label_to_name_map = {name: name for name in true_class_names}

    print("\n### 🔍 Lookup Diagnostics (Crucial for Debugging N/A values):")
    try:
        rfc_classes = rfc.classes_

        if all(isinstance(c, (int, np.integer)) for c in rfc_classes):
            class_label_to_name_map = {index: name for index, name in enumerate(true_class_names)}
            print(f"RFC Class Type: {type(rfc_classes[0])} (INTEGER)")
            print(f"First 5 RFC Classes (Predicted): {rfc_classes[:5]} (Integers)")
            print("\n**⚠️ Failsafe Mapping Activated: Model classes are integers!**")
            print(f"Mapping Index {rfc_classes[0]} -> Name: {class_label_to_name_map.get(rfc_classes[0], 'ERROR')}")
        else:
            print(f"RFC Class Type: {type(rfc_classes[0])} (STRING)")
            class_label_to_name_map = {str(c).strip(): str(c).strip() for c in rfc_classes}

    except Exception as e:
        print(f"Could not access rfc.classes_ for diagnostics ({e}). Assuming classes are strings.")

    try:
        print(f"First 5 Lookup Keys (Expected): {df['name_updated'].unique()[:5].tolist()}")
    except Exception:
        print("Could not access cafe_lookup_df index for diagnostics.")
    
    print("----------------------------------------------------\n")
    return class_label_to_name_map
