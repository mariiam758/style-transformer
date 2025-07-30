import textstat

def get_readability_scores(text):
    return {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "dale_chall_score": textstat.dale_chall_readability_score(text),
        "cefr_estimate": estimate_cefr_level(text)
    }

def estimate_cefr_level(text):
    # Simple heuristic using Flesch grade
    grade = textstat.flesch_kincaid_grade(text)
    if grade < 5:
        return "A1-A2"
    elif grade < 8:
        return "B1"
    elif grade < 11:
        return "B2"
    elif grade < 14:
        return "C1"
    else:
        return "C2"