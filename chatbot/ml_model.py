"""
ML model for disease prediction.
Uses Random Forest + confidence scores + top 3 predictions.
Reply style: Short, direct, confident (Style A).
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from django.conf import settings

from .disease_info import get_disease_info
from .data_generator import augment_data, AUGMENTED_PATH

# ===========================================================
# FILE PATHS
# ===========================================================
DATA_PATH  = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'symptoms.csv')
MODEL_PATH = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'model.pkl')

# Lower threshold = more willing to give a direct answer
# Only show "I'm not sure" if TRULY nothing matches
CONFIDENCE_THRESHOLD = 0.15

# ===========================================================
# CASUAL / NON-MEDICAL PHRASES
# Bot gives friendly redirect instead of trying to predict
# ===========================================================
CASUAL_PHRASES = [
    'hello', 'hi', 'hey', 'good morning', 'good evening',
    'good afternoon', 'good night', 'how are you', 'how r u',
    'whats up', "what's up", 'thanks', 'thank you', 'thankyou',
    'thank u', 'ok', 'okay', 'alright', 'fine', 'great',
    'bye', 'goodbye', 'see you', 'help', 'who are you',
    'what are you', 'what can you do', 'test', 'testing',
    'yes', 'no', 'yep', 'nope', 'sure', 'hmm', 'lol',
]


# ===========================================================
# TRAIN MODEL
# ===========================================================
def train_model():
    """
    Trains Random Forest on augmented dataset.
    Saves model + symptom list + class labels.
    """
    if not os.path.exists(AUGMENTED_PATH):
        print("🧬 Augmented data not found, generating...")
        augment_data(target_rows=8000)

    print("📚 Loading augmented dataset...")
    df = pd.read_csv(AUGMENTED_PATH)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    symptom_cols = list(X.columns)
    classes      = sorted(y.unique().tolist())

    print(f"✅ {len(df)} rows | {len(symptom_cols)} symptoms | {len(classes)} diseases")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🌳 Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
    )
    model.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc  = accuracy_score(y_test,  model.predict(X_test))
    print(f"📊 Train: {train_acc*100:.2f}% | Test: {test_acc*100:.2f}%")

    bundle = {
        'model':         model,
        'symptoms':      symptom_cols,
        'classes':       classes,
        'test_accuracy': test_acc,
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)

    print(f"✅ Model saved → {MODEL_PATH}")
    return bundle


# ===========================================================
# LOAD MODEL (cached in memory)
# ===========================================================
_cached_bundle = None

def load_model():
    global _cached_bundle
    if _cached_bundle is not None:
        return _cached_bundle
    if not os.path.exists(MODEL_PATH):
        print("⚠️ No model found — training now...")
        train_model()
    with open(MODEL_PATH, 'rb') as f:
        _cached_bundle = pickle.load(f)
    return _cached_bundle


# ===========================================================
# NORMALIZE SYMPTOM
# ===========================================================
def normalize_symptom(symptom):
    """
    'Skin Rash' → 'skin_rash'
    """
    return symptom.strip().lower().replace(' ', '_').replace('-', '_')


# ===========================================================
# CHECK IF CASUAL INPUT
# ===========================================================
def is_casual_input(text):
    """
    Returns True if the user typed a greeting/casual phrase
    instead of describing symptoms.
    """
    cleaned = text.strip().lower().rstrip('!?.').strip()
    return cleaned in CASUAL_PHRASES


# ===========================================================
# PREDICT DISEASE
# ===========================================================
def predict_disease(user_symptoms):
    """
    Returns top 3 predictions with confidence scores.

    Args:
        user_symptoms: list of str  e.g. ['fever', 'cough']

    Returns dict:
        top_disease    : str   best prediction
        confidence     : float 0-1
        top_3          : list  [{disease, confidence, info}]
        is_confident   : bool  confidence >= threshold
        matched_symptoms   : list
        unmatched_symptoms : list
        error          : str | None
    """
    bundle      = load_model()
    model       = bundle['model']
    all_symptoms = bundle['symptoms']
    classes     = bundle['classes']

    user_set = {normalize_symptom(s) for s in user_symptoms if s.strip()}
    matched   = [s for s in user_set if s in all_symptoms]
    unmatched = [s for s in user_set if s not in all_symptoms]

    if not matched:
        return {
            'top_disease':         None,
            'confidence':          0.0,
            'top_3':               [],
            'is_confident':        False,
            'matched_symptoms':    [],
            'unmatched_symptoms':  list(unmatched),
            'error': 'no_match',
        }

    input_vector  = np.array([
        [1 if s in user_set else 0 for s in all_symptoms]
    ])
    probabilities = model.predict_proba(input_vector)[0]
    top_indices   = np.argsort(probabilities)[::-1][:3]

    top_3 = []
    for idx in top_indices:
        disease = classes[idx]
        conf    = float(probabilities[idx])
        if conf > 0.01:
            top_3.append({
                'disease':    disease,
                'confidence': round(conf, 3),
                'info':       get_disease_info(disease),
            })

    top_disease    = top_3[0]['disease']    if top_3 else None
    top_confidence = top_3[0]['confidence'] if top_3 else 0.0

    return {
        'top_disease':         top_disease,
        'confidence':          top_confidence,
        'top_3':               top_3,
        'is_confident':        top_confidence >= CONFIDENCE_THRESHOLD,
        'matched_symptoms':    matched,
        'unmatched_symptoms':  unmatched,
        'error':               None,
    }


# ===========================================================
# BUILD REPLY  —  Style A (Short, Direct, Confident)
# ===========================================================
def build_caring_reply(prediction_result, original_message=''):
    """
    Builds a short, direct, professional reply.

    Style A format:
        Based on your symptoms (X, Y), you may have DISEASE (confidence%).
        💡 Short description.
        🔍 Other possibilities: B, C  (if any)
        ⚠️  Severity note (if high)
        ⚕️  Please consult a doctor for proper diagnosis.
    """

    # ── Case 1: Casual / greeting input ──────────────────────
    if prediction_result.get('error') == 'casual':
        return (
            "Hello! 👋 I'm your AI health assistant.\n"
            "Please describe your symptoms and I'll help you understand what might be going on.\n\n"
            "Example: \"I have fever, cough, and headache.\""
        )

    # ── Case 2: No symptoms recognized at all ────────────────
    if prediction_result.get('error') == 'no_match':
        # Still try to give a helpful answer — don't leave user confused
        return (
            "I wasn't able to recognize specific symptoms from your message.\n\n"
            "Please try describing your physical symptoms clearly.\n"
            "Example: \"I have fever, sore throat, and body aches.\"\n\n"
            "⚕️ If you're feeling very unwell, please contact a doctor immediately."
        )

    # ── Case 3: Low confidence — still give best guess ───────
    # (never leave user with no answer)
    top         = prediction_result['top_3'][0]
    others      = prediction_result['top_3'][1:]
    matched     = ', '.join(prediction_result['matched_symptoms'])
    conf_pct    = int(top['confidence'] * 100)
    disease     = top['disease'].strip()
    description = top['info']['description']
    advice      = top['info']['advice']
    severity    = top['info'].get('severity', 'medium')

    # ── Build the reply ───────────────────────────────────────
    lines = []

    # Line 1: Main prediction
    lines.append(
        f"Based on your symptoms ({matched}), "
        f"you may have **{disease}** ({conf_pct}% confidence)."
    )

    # Line 2: What is it
    lines.append(f"\n💡 {description}")

    # Line 3: What to do
    lines.append(f"💊 {advice}")

    # Line 4: Other possibilities (if any)
    if others:
        other_names = [
            f"{o['disease'].strip()} ({int(o['confidence']*100)}%)"
            for o in others
        ]
        lines.append(f"\n🔍 Other possibilities: {', '.join(other_names)}")

    # Line 5: Severity warning
    if severity == 'high':
        lines.append(
            "\n⚠️ This condition can be serious. "
            "Please see a doctor as soon as possible."
        )

    # Line 6: Always end with disclaimer
    lines.append("\n⚕️ Please consult a doctor for proper diagnosis.")

    return '\n'.join(lines)


# ===========================================================
# SHOULD BOOKING POPUP SHOW?
# ===========================================================
def is_symptom_message(prediction_result):
    """
    Show booking popup only when we made a real prediction.
    Not for casual input or unrecognized symptoms.
    """
    return (
        prediction_result.get('error') is None
        and prediction_result.get('top_disease') is not None
    )