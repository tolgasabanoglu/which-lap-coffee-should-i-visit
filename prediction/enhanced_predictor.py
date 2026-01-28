import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class EnhancedCafePredictor:
    """
    Enhanced cafe prediction system with confidence-based filtering
    and probability-based suitability scoring.
    """

    def __init__(self, model, label_encoder, cafe_lookup_df, friendly_name_col='name'):
        """
        Initialize the enhanced predictor.

        Args:
            model: Trained RandomForestClassifier
            label_encoder: Fitted LabelEncoder for cafe names
            cafe_lookup_df: DataFrame with cafe information (indexed by name_updated)
            friendly_name_col: Column name for display names
        """
        self.model = model
        self.label_encoder = label_encoder
        self.cafe_lookup_df = cafe_lookup_df
        self.friendly_name_col = friendly_name_col

    def predict_with_confidence(
        self,
        profile_df: pd.DataFrame,
        top_n: int = 5,
        min_confidence: float = 0.10
    ) -> List[Dict]:
        """
        Predict cafe recommendations with confidence filtering.

        Args:
            profile_df: DataFrame with mood/weather features (single row)
            top_n: Number of top recommendations to return
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of dictionaries with recommendation details
        """
        # Get probabilities for all cafes
        probabilities = self.model.predict_proba(profile_df)[0]

        # Get all cafe indices sorted by probability
        sorted_indices = np.argsort(probabilities)[::-1]

        recommendations = []

        for idx in sorted_indices[:top_n]:
            confidence = probabilities[idx]

            # Skip if below confidence threshold
            if confidence < min_confidence:
                continue

            cafe_label = self.model.classes_[idx]

            # Handle integer class labels (failsafe mapping)
            if isinstance(cafe_label, (int, np.integer)):
                cafe_name_updated = self.label_encoder.classes_[cafe_label]
            else:
                cafe_name_updated = str(cafe_label).strip()

            # Lookup cafe details
            if cafe_name_updated in self.cafe_lookup_df.index:
                friendly_name = self.cafe_lookup_df.loc[cafe_name_updated, self.friendly_name_col]
                address = self.cafe_lookup_df.loc[cafe_name_updated, 'address']

                recommendations.append({
                    'rank': len(recommendations) + 1,
                    'name': friendly_name,
                    'address': address,
                    'suitability_score': confidence * 100,
                    'confidence_level': self._classify_confidence(confidence),
                    'probability': confidence
                })
            else:
                # Fallback if lookup fails
                recommendations.append({
                    'rank': len(recommendations) + 1,
                    'name': cafe_name_updated,
                    'address': 'N/A',
                    'suitability_score': confidence * 100,
                    'confidence_level': self._classify_confidence(confidence),
                    'probability': confidence
                })

        return recommendations

    def predict_all_moods(
        self,
        mood_profiles: Dict[str, pd.DataFrame],
        top_n: int = 3,
        min_confidence: float = 0.10
    ) -> Dict[str, List[Dict]]:
        """
        Predict recommendations for multiple mood profiles.

        Args:
            mood_profiles: Dictionary of {mood_name: profile_dataframe}
            top_n: Number of recommendations per mood
            min_confidence: Minimum confidence threshold

        Returns:
            Dictionary of {mood_name: recommendations_list}
        """
        results = {}

        for mood_name, profile_df in mood_profiles.items():
            recommendations = self.predict_with_confidence(
                profile_df,
                top_n=top_n,
                min_confidence=min_confidence
            )
            results[mood_name] = recommendations

        return results

    def get_mood_summary(
        self,
        mood_profiles: Dict[str, pd.DataFrame],
        top_n: int = 2
    ) -> pd.DataFrame:
        """
        Generate a summary table of top recommendations for each mood.

        Args:
            mood_profiles: Dictionary of mood profiles
            top_n: Number of top cafes to include per mood

        Returns:
            DataFrame with summary of recommendations
        """
        summary_data = {
            'Mood': [],
            'Top Recommendation': [],
            'Address': [],
            'Suitability Score': [],
            'Confidence Level': []
        }

        all_results = self.predict_all_moods(mood_profiles, top_n=top_n, min_confidence=0.05)

        for mood_name, recommendations in all_results.items():
            if recommendations:
                top_rec = recommendations[0]
                summary_data['Mood'].append(mood_name)
                summary_data['Top Recommendation'].append(top_rec['name'])
                summary_data['Address'].append(top_rec['address'])
                summary_data['Suitability Score'].append(f"{top_rec['suitability_score']:.1f}%")
                summary_data['Confidence Level'].append(top_rec['confidence_level'])
            else:
                summary_data['Mood'].append(mood_name)
                summary_data['Top Recommendation'].append('No confident match')
                summary_data['Address'].append('N/A')
                summary_data['Suitability Score'].append('N/A')
                summary_data['Confidence Level'].append('N/A')

        return pd.DataFrame(summary_data)

    def _classify_confidence(self, confidence: float) -> str:
        """
        Classify confidence level into categories.

        Args:
            confidence: Probability value (0-1)

        Returns:
            Confidence level string
        """
        if confidence >= 0.50:
            return 'High'
        elif confidence >= 0.30:
            return 'Medium'
        elif confidence >= 0.15:
            return 'Low'
        else:
            return 'Very Low'

    def explain_prediction(
        self,
        profile_df: pd.DataFrame,
        cafe_name: str
    ) -> Dict:
        """
        Explain why a particular cafe was recommended for a profile.

        Args:
            profile_df: Feature profile
            cafe_name: Name of the cafe to explain

        Returns:
            Dictionary with explanation details
        """
        # Get feature importances from model
        feature_importances = pd.Series(
            self.model.feature_importances_,
            index=profile_df.columns
        ).sort_values(ascending=False)

        # Get prediction probability
        probabilities = self.model.predict_proba(profile_df)[0]
        predicted_idx = np.argmax(probabilities)
        predicted_cafe = self.model.classes_[predicted_idx]

        return {
            'predicted_cafe': predicted_cafe,
            'confidence': probabilities[predicted_idx],
            'top_features': feature_importances.head(3).to_dict(),
            'profile_values': profile_df.iloc[0].to_dict()
        }


def format_recommendations_table(recommendations: List[Dict]) -> pd.DataFrame:
    """
    Format recommendations as a clean DataFrame.

    Args:
        recommendations: List of recommendation dictionaries

    Returns:
        Formatted DataFrame
    """
    if not recommendations:
        return pd.DataFrame({'Message': ['No confident recommendations found']})

    df = pd.DataFrame(recommendations)
    df = df[['rank', 'name', 'address', 'suitability_score', 'confidence_level']]
    df.columns = ['Rank', 'Cafe Name', 'Address', 'Suitability (%)', 'Confidence']
    return df


def print_recommendations_report(
    mood_name: str,
    recommendations: List[Dict],
    profile_df: pd.DataFrame
):
    """
    Print a formatted report of recommendations.

    Args:
        mood_name: Name of the mood profile
        recommendations: List of recommendations
        profile_df: Feature profile used
    """
    print(f"\n{'='*70}")
    print(f"Recommendations for: {mood_name}")
    print(f"{'='*70}")

    if not recommendations:
        print("\nNo confident recommendations found for this profile.")
        print("Consider adjusting the minimum confidence threshold or mood features.")
        return

    print(f"\nFound {len(recommendations)} suitable cafe(s):\n")

    for rec in recommendations:
        print(f"{rec['rank']}. {rec['name']}")
        print(f"   Address: {rec['address']}")
        print(f"   Suitability: {rec['suitability_score']:.1f}%")
        print(f"   Confidence: {rec['confidence_level']}")
        print()

    print("\nProfile Features Used:")
    for feature, value in profile_df.iloc[0].items():
        print(f"  - {feature}: {value:.2f}")
    print()
