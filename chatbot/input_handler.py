"""
Input handler for chatbot messages.
Cleans text, fixes typos, extracts symptoms,
and detects casual (non-medical) input.
"""

import re

try:
    from spellchecker import SpellChecker
    spell = SpellChecker()
    SPELL_CHECK_AVAILABLE = True
except ImportError:
    SPELL_CHECK_AVAILABLE = False
    print("⚠️ pyspellchecker not installed. Run: pip install pyspellchecker")


# ── Medical terms — never auto-correct these ─────────────────
MEDICAL_TERMS = {
    'nausea', 'fatigue', 'malaise', 'diarrhea', 'vomiting',
    'dyspnea', 'vertigo', 'tinnitus', 'myalgia', 'dysphagia',
    'haematuria', 'pyrexia', 'syncope', 'oedema', 'polyuria',
    'polydipsia', 'pruritus', 'jaundice', 'cyanosis', 'pallor',
    'tachycardia', 'bradycardia', 'hypertension', 'hypotension',
    'headache', 'stomachache', 'backache', 'toothache',
    'breathlessness', 'dizziness', 'chills', 'sweating',
    'sneezing', 'coughing', 'bloating', 'cramping',
    'redness', 'swelling', 'itching', 'numbness', 'tingling',
    'dengue', 'malaria', 'typhoid', 'cholera', 'tuberculosis',
    'hepatitis', 'pneumonia', 'bronchitis', 'asthma', 'psoriasis',
    'eczema', 'migraine', 'arthritis', 'diabetes',
}

# ── Manual corrections for common typos ──────────────────────
MANUAL_CORRECTIONS = {
    'fiver':       'fever',
    'fevr':        'fever',
    'fver':        'fever',
    'coff':        'cough',
    'cogh':        'cough',
    'headach':     'headache',
    'stomack':     'stomach',
    'stomech':     'stomach',
    'diarea':      'diarrhea',
    'diarrhoe':    'diarrhea',
    'vommit':      'vomiting',
    'vomitting':   'vomiting',
    'tierd':       'tired',
    'fateigue':    'fatigue',
    'fatiuge':     'fatigue',
    'sweting':     'sweating',
    'burining':    'burning',
    'painfull':    'painful',
    'itch':        'itching',
    'dizzy':       'dizziness',
    'runny nose':  'runny_nose',
    'chest pain':  'chest_pain',
    'sore throat': 'sore_throat',
    'back pain':   'back_pain',
    'stomach pain':'stomach_pain',
    'body ache':   'muscle_pain',
    'body aches':  'muscle_pain',
}

# ── Phrases that indicate casual (non-medical) input ─────────
CASUAL_PATTERNS = [
    r'^(hi+|hey+|hello+|helo+|hii+)\b',
    r'^(good\s+(morning|evening|afternoon|night))',
    r'^how\s+are\s+(you|u)',
    r'^(what\'?s?\s+up|wassup|sup)\b',
    r'^(thanks?|thank\s+(you|u)|thankyou|thx)\b',
    r'^(ok+|okay|alright|fine|great|cool|nice)\b',
    r'^(bye+|goodbye|see\s+you|cya)\b',
    r'^(yes|no|yep|nope|sure|hmm+|lol)\b',
    r'^(test+|testing|ping)\b',
    r'^(who|what)\s+are\s+you\b',
    r'^what\s+can\s+you\s+do\b',
    r'^help\b$',
]


def is_casual_message(text):
    """
    Returns True if the message is a greeting/casual phrase,
    not a symptom description.
    """
    cleaned = text.strip().lower().rstrip('!?.').strip()

    # Check exact matches first
    from .ml_model import CASUAL_PHRASES
    if cleaned in CASUAL_PHRASES:
        return True

    # Check regex patterns
    for pattern in CASUAL_PATTERNS:
        if re.match(pattern, cleaned):
            return True

    # If message is very short (1-2 words) and no known symptom → likely casual
    words = cleaned.split()
    if len(words) <= 2:
        has_symptom = any(w in MEDICAL_TERMS for w in words)
        if not has_symptom:
            return True

    return False


def clean_input(raw_text):
    """
    Main cleaning function.
    1. Strip + lowercase
    2. Apply manual corrections
    3. Apply spell checker
    Returns cleaned string or '' if empty.
    """
    if not raw_text:
        return ''

    text = raw_text.strip().lower()
    if not text:
        return ''

    # Apply manual corrections
    for wrong, correct in MANUAL_CORRECTIONS.items():
        text = text.replace(wrong, correct)

    # Apply spell checker
    if SPELL_CHECK_AVAILABLE:
        text = _spell_correct_text(text)

    return text


def _spell_correct_text(text):
    """Word-by-word spell correction with medical term protection."""
    tokens = re.split(r'([\s,;]+)', text)
    corrected = []

    for token in tokens:
        if re.match(r'^[\s,;]+$', token):
            corrected.append(token)
            continue

        word = token.strip()

        if len(word) <= 2:
            corrected.append(token)
            continue
        if word.isdigit():
            corrected.append(token)
            continue
        if word in MEDICAL_TERMS:
            corrected.append(token)
            continue
        if '_' in word:
            corrected.append(token)
            continue

        correction = spell.correction(word)
        if correction and correction != word:
            corrected.append(correction)
        else:
            corrected.append(token)

    return ''.join(corrected)


def extract_symptoms(cleaned_text):
    """
    Extracts individual symptom terms from cleaned text.

    Handles:
      "fever, cough, headache"          → ['fever', 'cough', 'headache']
      "I have fever and cough"          → ['fever', 'cough']
      "fever and sore throat"           → ['fever', 'sore_throat']
    """
    if not cleaned_text:
        return []

    text = cleaned_text.lower()

    # Remove filler phrases
    fillers = [
        "i have", "i've got", "i got", "i am having", "i am feeling",
        "i feel", "i'm feeling", "i'm having", "suffering from",
        "experiencing", "dealing with", "my symptoms are",
        "i've been having", "i have been having", "i notice",
        "symptoms include", "include", "such as", "since",
        "for the past", "past few days", "few days", "i also have",
        "also have", "also", "along with", "as well as",
    ]
    for phrase in fillers:
        text = text.replace(phrase, ' ')

    # Replace 'and' / '+' / ';' with commas
    text = re.sub(r'\band\b', ',', text)
    text = re.sub(r'[+;]', ',', text)

    # Split by commas
    raw = text.split(',')
    symptoms = []

    for s in raw:
        clean = s.strip()
        # Remove leading articles
        clean = re.sub(r'^(a|an|the)\s+', '', clean)
        # Remove duration words e.g. "for 2 days"
        clean = re.sub(r'\bfor\s+\d+\s+\w+', '', clean).strip()
        # Replace spaces with underscores
        clean = clean.replace(' ', '_')
        # Remove trailing underscores/punctuation
        clean = clean.strip('_.,!?')
        if len(clean) >= 3:
            symptoms.append(clean)

    return symptoms