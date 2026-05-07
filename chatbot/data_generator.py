"""
Synthetic data generator.
Boosts your existing symptoms.csv from ~4,920 rows to ~8,000+ rows
by creating realistic variations of existing samples.

This makes the ML model more robust to slight symptom variations.
"""

import os
import random
import pandas as pd
import numpy as np
from django.conf import settings

DATA_PATH = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'symptoms.csv')
AUGMENTED_PATH = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'symptoms_augmented.csv')


def augment_data(target_rows=8000, noise_chance=0.05):
    """
    Reads symptoms.csv and creates a larger augmented dataset.
    
    Strategy:
    - Keep all original rows (preserves correctness)
    - For each disease, create variations by:
        * Randomly flipping a small % of symptoms (simulates incomplete reporting)
        * This simulates real users who might forget to mention 1-2 symptoms
    
    Args:
        target_rows: how many total rows we want
        noise_chance: probability of flipping each symptom (default 5%)
    """
    print("📚 Loading original dataset...")
    df = pd.read_csv(DATA_PATH)

    # Drop weird "Unnamed" columns if present
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Separate features and labels
    X = df.iloc[:, :-1]    # all symptom columns
    y = df.iloc[:, -1]     # the disease column
    symptom_cols = X.columns.tolist()

    print(f"✅ Original: {len(df)} rows, {len(symptom_cols)} symptoms, {y.nunique()} diseases")

    # How many synthetic rows do we need?
    needed = max(0, target_rows - len(df))
    print(f"🧬 Generating {needed} synthetic rows...")

    if needed == 0:
        print("✅ Already enough data, skipping augmentation.")
        df.to_csv(AUGMENTED_PATH, index=False)
        return AUGMENTED_PATH

    synthetic_rows = []
    rng = np.random.default_rng(seed=42)  # reproducible randomness

    # For each new row, pick a real row and add slight noise
    for i in range(needed):
        # Pick a random existing row as a "template"
        template_idx = rng.integers(0, len(df))
        template_features = X.iloc[template_idx].values.copy()
        template_label = y.iloc[template_idx]

        # Flip some symptoms randomly (small noise)
        for j in range(len(template_features)):
            if rng.random() < noise_chance:
                # 70% chance to remove a symptom (more common: people forget)
                # 30% chance to add a symptom (less common: false alarm)
                if template_features[j] == 1 and rng.random() < 0.7:
                    template_features[j] = 0
                elif template_features[j] == 0 and rng.random() < 0.3:
                    template_features[j] = 1

        # Build the new row
        new_row = list(template_features) + [template_label]
        synthetic_rows.append(new_row)

    # Convert synthetic data to DataFrame
    synthetic_df = pd.DataFrame(synthetic_rows, columns=symptom_cols + ['prognosis'])

    # Combine original + synthetic
    augmented_df = pd.concat([df, synthetic_df], ignore_index=True)

    # Shuffle rows so model doesn't see all originals first
    augmented_df = augmented_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save to new file (keeps original CSV intact)
    augmented_df.to_csv(AUGMENTED_PATH, index=False)

    print(f"✅ Augmented dataset: {len(augmented_df)} rows")
    print(f"💾 Saved to: {AUGMENTED_PATH}")
    return AUGMENTED_PATH


if __name__ == "__main__":
    # This lets you run it directly with: python chatbot/data_generator.py
    augment_data()