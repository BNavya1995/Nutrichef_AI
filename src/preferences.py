import os
import json

PREFS_FILE = os.path.join("data", "user_preferences.json")

def initialize_preferences():
    """Ensures the data directory and preference file exist safely upon engine startup."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "w") as f:
            json.dump({"liked_meals": [], "disliked_meals": [], "feedback_history": []}, f)

def save_meal_feedback(meal_name: str, rating: int, comment: str = ""):
    """Saves user rating metrics into local JSON storage matrix logs."""
    initialize_preferences()
    with open(PREFS_FILE, "r") as f:
        data = json.load(f)
        
    log_entry = {"meal_name": meal_name.lower(), "rating": rating, "comment": comment.lower()}
    data["feedback_history"].append(log_entry)
    
    # Categorize explicitly for instant LLM prompt injection mapping rules
    if rating >= 4 and log_entry["meal_name"] not in data["liked_meals"]:
        data["liked_meals"].append(log_entry["meal_name"])
    elif rating <= 2 and log_entry["meal_name"] not in data["disliked_meals"]:
        data["disliked_meals"].append(log_entry["meal_name"])
        
    with open(PREFS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_preference_instructions() -> str:
    """Compiles profile learning trends directly into clear rules for the LLM context prompt."""
    if not os.path.exists(PREFS_FILE):
        return ""
    try:
        with open(PREFS_FILE, "r") as f:
            data = json.load(f)
        
        rules = []
        if data.get("liked_meals"):
            rules.append(f"Highly preferred meal patterns to emulate or build variations of: {', '.join(data['liked_meals'])}.")
        if data.get("disliked_meals"):
            rules.append(f"CRITICAL DISLIKE RULES: Avoid regenerating these exact recipes or heavy variations of them: {', '.join(data['disliked_meals'])}.")
            
        return " ".join(rules)
    except Exception:
        return ""