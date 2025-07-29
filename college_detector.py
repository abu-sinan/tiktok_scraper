# utils/college_detector.py

def detect_college(text):
    colleges = [
        "ucla", "fsu", "georgia tech", "asu", "harvard", "yale",
        "berkeley", "mit", "stanford", "usc", "duke", "nyu"
    ]
    for college in colleges:
        if college.lower() in text.lower():
            return college
    return "Unknown"
