"""
Disease information dictionary.
Used to enrich bot replies with friendly descriptions and advice.
"""

DISEASE_INFO = {
    "Fungal infection": {
        "description": "A skin infection caused by fungi, often itchy and red.",
        "advice": "Keep the affected area clean and dry. Avoid sharing towels.",
        "severity": "low",
    },
    "Allergy": {
        "description": "An immune reaction to substances like pollen, dust, or food.",
        "advice": "Identify and avoid the trigger. Antihistamines may help.",
        "severity": "low",
    },
    "GERD": {
        "description": "Acid reflux that causes heartburn and chest discomfort.",
        "advice": "Avoid spicy/oily food. Don't lie down right after eating.",
        "severity": "medium",
    },
    "Chronic cholestasis": {
        "description": "A liver condition where bile flow is reduced or blocked.",
        "advice": "Requires medical evaluation. Avoid alcohol and fatty foods.",
        "severity": "high",
    },
    "Drug Reaction": {
        "description": "An adverse reaction to a medication.",
        "advice": "Stop the suspected drug and consult a doctor immediately.",
        "severity": "high",
    },
    "Peptic ulcer diseae": {
        "description": "Sores in the stomach lining causing pain and discomfort.",
        "advice": "Avoid spicy food, alcohol, and NSAIDs. See a doctor.",
        "severity": "medium",
    },
    "AIDS": {
        "description": "A serious immune system disease caused by HIV.",
        "advice": "Requires immediate medical care and lifelong treatment.",
        "severity": "high",
    },
    "Diabetes ": {
        "description": "A condition where blood sugar levels are too high.",
        "advice": "Monitor blood sugar, eat balanced meals, and exercise regularly.",
        "severity": "medium",
    },
    "Gastroenteritis": {
        "description": "Inflammation of the stomach and intestines (stomach flu).",
        "advice": "Stay hydrated. Eat bland foods. Rest well.",
        "severity": "low",
    },
    "Bronchial Asthma": {
        "description": "A condition causing breathing difficulty and wheezing.",
        "advice": "Avoid triggers like dust and smoke. Use inhaler if prescribed.",
        "severity": "medium",
    },
    "Hypertension ": {
        "description": "High blood pressure that can affect the heart and brain.",
        "advice": "Reduce salt intake, exercise, and manage stress.",
        "severity": "medium",
    },
    "Migraine": {
        "description": "A severe headache, often with nausea and light sensitivity.",
        "advice": "Rest in a dark, quiet room. Stay hydrated.",
        "severity": "medium",
    },
    "Cervical spondylosis": {
        "description": "Wear and tear of the neck's spinal disks.",
        "advice": "Maintain good posture. Gentle neck exercises may help.",
        "severity": "medium",
    },
    "Paralysis (brain hemorrhage)": {
        "description": "Loss of muscle function due to brain bleeding — a medical emergency.",
        "advice": "Call emergency services immediately!",
        "severity": "high",
    },
    "Jaundice": {
        "description": "Yellowing of skin and eyes due to liver issues.",
        "advice": "See a doctor for liver function tests. Avoid alcohol.",
        "severity": "high",
    },
    "Malaria": {
        "description": "A mosquito-borne infection causing fever and chills.",
        "advice": "Requires immediate medical treatment. Use mosquito nets.",
        "severity": "high",
    },
    "Chicken pox": {
        "description": "A viral infection causing itchy blisters all over the body.",
        "advice": "Stay isolated. Avoid scratching. Drink fluids.",
        "severity": "medium",
    },
    "Dengue": {
        "description": "A mosquito-borne viral disease causing high fever and body pain.",
        "advice": "Stay hydrated. Seek medical care urgently.",
        "severity": "high",
    },
    "Typhoid": {
        "description": "A bacterial infection from contaminated food or water.",
        "advice": "Requires antibiotics. Stay hydrated and rest.",
        "severity": "high",
    },
    "hepatitis A": {
        "description": "A liver infection from contaminated food or water.",
        "advice": "Rest, hydration, and avoid alcohol. Consult a doctor.",
        "severity": "medium",
    },
    "Hepatitis B": {
        "description": "A serious liver infection caused by the hepatitis B virus.",
        "advice": "Requires medical treatment. Get vaccinated to prevent.",
        "severity": "high",
    },
    "Hepatitis C": {
        "description": "A viral infection that causes liver inflammation.",
        "advice": "Requires antiviral treatment. See a specialist.",
        "severity": "high",
    },
    "Hepatitis D": {
        "description": "A liver infection that occurs only with hepatitis B.",
        "advice": "Requires immediate medical care.",
        "severity": "high",
    },
    "Hepatitis E": {
        "description": "A liver infection often spread through contaminated water.",
        "advice": "Rest, hydrate, and avoid alcohol. See a doctor.",
        "severity": "medium",
    },
    "Alcoholic hepatitis": {
        "description": "Liver inflammation caused by heavy alcohol consumption.",
        "advice": "Stop drinking alcohol immediately. See a doctor.",
        "severity": "high",
    },
    "Tuberculosis": {
        "description": "A serious bacterial infection that mainly affects the lungs.",
        "advice": "Requires long-term antibiotic treatment. Wear a mask.",
        "severity": "high",
    },
    "Common Cold": {
        "description": "A mild viral infection of the nose and throat.",
        "advice": "Rest, drink fluids, and use over-the-counter remedies.",
        "severity": "low",
    },
    "Pneumonia": {
        "description": "Infection that inflames air sacs in the lungs.",
        "advice": "Requires antibiotics or antivirals. See a doctor urgently.",
        "severity": "high",
    },
    "Dimorphic hemmorhoids(piles)": {
        "description": "Swollen veins in the lower rectum or anus.",
        "advice": "Eat fiber-rich food. Drink water. Avoid straining.",
        "severity": "low",
    },
    "Heart attack": {
        "description": "A serious condition where blood flow to the heart is blocked.",
        "advice": "Call emergency services immediately! Chew aspirin if able.",
        "severity": "high",
    },
    "Varicose veins": {
        "description": "Enlarged, twisted veins, usually in the legs.",
        "advice": "Avoid standing for long. Elevate legs when resting.",
        "severity": "low",
    },
    "Hypothyroidism": {
        "description": "When the thyroid gland doesn't produce enough hormones.",
        "advice": "Requires daily medication. Regular blood tests needed.",
        "severity": "medium",
    },
    "Hyperthyroidism": {
        "description": "When the thyroid gland produces too much hormone.",
        "advice": "See a doctor for medication or treatment.",
        "severity": "medium",
    },
    "Hypoglycemia": {
        "description": "Low blood sugar — can cause shakiness and confusion.",
        "advice": "Eat or drink something sugary immediately.",
        "severity": "medium",
    },
    "Osteoarthristis": {
        "description": "Joint disease causing pain and stiffness, especially in older adults.",
        "advice": "Gentle exercise, weight management, and pain relief.",
        "severity": "medium",
    },
    "Arthritis": {
        "description": "Inflammation of the joints causing pain and stiffness.",
        "advice": "Stay active gently. Anti-inflammatory medication may help.",
        "severity": "medium",
    },
    "(vertigo) Paroymsal  Positional Vertigo": {
        "description": "A condition causing brief episodes of dizziness.",
        "advice": "Avoid sudden head movements. See a doctor for exercises.",
        "severity": "low",
    },
    "Acne": {
        "description": "A skin condition causing pimples and blackheads.",
        "advice": "Wash face gently. Avoid squeezing pimples.",
        "severity": "low",
    },
    "Urinary tract infection": {
        "description": "An infection in any part of the urinary system.",
        "advice": "Drink lots of water. Antibiotics may be needed.",
        "severity": "medium",
    },
    "Psoriasis": {
        "description": "A skin disease causing red, scaly patches.",
        "advice": "Use prescribed creams. Avoid skin triggers.",
        "severity": "medium",
    },
    "Impetigo": {
        "description": "A contagious skin infection causing red sores.",
        "advice": "Keep area clean. Antibiotics usually needed.",
        "severity": "medium",
    },
}


def get_disease_info(disease_name):
    """
    Look up a disease and return its info.
    If not found, returns a generic fallback.
    """
    info = DISEASE_INFO.get(disease_name)
    if info:
        return info
    return {
        "description": "A medical condition that may require attention.",
        "advice": "Please consult a healthcare professional.",
        "severity": "medium",
    }