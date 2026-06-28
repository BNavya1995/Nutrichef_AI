from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import ollama
from preferences import load_preference_instructions, save_meal_feedback, initialize_preferences
from recommender import MLRecipeRecommender

app = FastAPI(title="NutriChef AI - Local Llama 3 Core Engine")

initialize_preferences()
ml_recommender = MLRecipeRecommender()

class FullDayPlanRequest(BaseModel):
    user_name: str
    age: int
    weight: float
    height: float = 165.0  # cm, default 165 if not provided
    ingredients: str
    dietary_restriction: Optional[str] = None
    target_slot: Optional[str] = "all"
    health_goal: Optional[str] = "Maintenance"

# ⚡ NEW: Form schema mapping out incoming user ratings blocks
class FeedbackRequest(BaseModel):
    meal_name: str
    rating: int
    comment: Optional[str] = ""

@app.post("/feedback")
def log_user_feedback(payload: FeedbackRequest):
    try:
        save_meal_feedback(payload.meal_name, payload.rating, payload.comment)
        return {"success": True, "message": "Preference trends updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend")
def recommend_via_local_llama(payload: FullDayPlanRequest):
    try:
        print(f"🤖 Booting local Llama 3 generation loop for: {payload.user_name}")
        
        # Mifflin-St Jeor BMR (female formula; height now from user input)
        bmr = int(10 * payload.weight + 6.25 * payload.height - 5 * payload.age - 161)
        
        # ML Layer: get top ingredient-matched recipes to seed the LLM with better context
        ml_suggestions = []
        try:
            ml_suggestions = ml_recommender.predict_recipes(
                payload.ingredients,
                dietary_restriction=payload.dietary_restriction,
                top_n=5
            )
        except Exception:
            pass  # ML layer is optional; LLM fallback handles it
        
        ml_context = ""
        if ml_suggestions:
            names = [r['name'] for r in ml_suggestions]
            ml_context = f"ML-matched recipes from pantry scan (use these as inspiration): {', '.join(names)}."
        
        # ⚡ NEW: Load learning preference constraints dynamically from JSON history file
        learned_history_rules = load_preference_instructions()
        
        system_instruction = (
    "You are a strict, automated AI nutritionist that outputs data ONLY in valid JSON. "
    "For every meal object requested, you must calculate and provide explicit numeric estimations for: "
    "'calories' (integer), 'protein' (string), 'carbs' (string), and 'fats' (string). "
    "CRITICAL STEP RULE: In the 'preparation' text string, you must explicitly mention the exact "
    "quantities used for all seasoning elements (such as salt, turmeric, and chile powder) directly within the cooking steps."
    "Never include conversational text, preamble, or markdown code block backticks outside the JSON object structure."
)
        
        user_prompt = f"""
        User Parameters:
        - Name: {payload.user_name}
        - Age: {payload.age} Years
        - Weight: {payload.weight} Kg
        - Dietary Goal: Balance a {bmr} kcal daily target baseline
        - Style Preference: {payload.dietary_restriction}
        - Available Kitchen Pantry: {payload.ingredients}
        
        Adaptive Learning Feedback Loop Rules:
        - {learned_history_rules if learned_history_rules else "No historical feedback logged yet. Generate native balanced combinations."}
        
        ML Pantry Match Suggestions:
        - {ml_context if ml_context else "No ML pre-filter available. Use pantry ingredients directly."}
        
        Task:
        Generate exactly 3 unique, completely non-repeating meals for the day (morning breakfast, afternoon lunch, evening snack/dinner) optimized for the user's explicit historical preference trends using the available pantry ingredients.
        
        You must return EXACTLY this JSON structure structure outline and nothing else:
        {{
            "morning": {{ "name": "Name", "ingredients": "items", "preparation": "steps", "calories": 350, "protein": "20g", "carbs": "45g", "fats": "8g", "ml_confidence_score": 0.95 }},
            "afternoon": {{ "name": "Name", "ingredients": "items", "preparation": "steps", "calories": 600, "protein": "35g", "carbs": "70g", "fats": "15g", "ml_confidence_score": 0.90 }},
            "evening": {{ "name": "Name", "ingredients": "items", "preparation": "steps", "calories": 500, "protein": "30g", "carbs": "50g", "fats": "12g", "ml_confidence_score": 0.85 }}
        }}
        """
        
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': user_prompt}
            ],
            options={'temperature': 0.45, 'presence_penalty': 0.6, 'top_p': 0.6}
        )
        
        response_text = response['message']['content'].strip()
        
        # Strip markdown code fences if LLM wraps output in ```json ... ```
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Extract first JSON object if there's any preamble text
        brace_start = response_text.find('{')
        brace_end = response_text.rfind('}')
        if brace_start != -1 and brace_end != -1:
            response_text = response_text[brace_start:brace_end + 1]
        
        try:
            structured_plan = json.loads(response_text)
        except json.JSONDecodeError as parse_err:
            raise HTTPException(
                status_code=500,
                detail=f"LLM returned malformed JSON: {str(parse_err)}. Raw output: {response_text[:300]}"
            )
        
        return {
            "success": True,
            "user_metadata": {
                "user_name": payload.user_name,
                "target_calories": f"{bmr} kcal/day target ()"
            },
            "full_day_plan": structured_plan
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))