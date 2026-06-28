import os
import pandas as pd
import numpy as np

class MLRecipeRecommender:
    def __init__(self, data_path="data/cleaned_recipes.csv"):
        self.data_path = data_path
        self.df = None
        
        # 🌾 Common ingredients users shouldn't have to explicitly type out
        self.PANTRY_STAPLES = {
            'water', 'salt', 'oil', 'ghee', 'turmeric', 'chile', 'chiles', 
            'powder', 'garam', 'masala', 'cumin', 'seeds', 'ginger', 'garlic', 
            'paste', 'black', 'pepper', 'coriander', 'leaves'
        }
        
    def load_artifacts(self):
        """Loads processed recipes from the database cache."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Missing processed data cache at {self.data_path}. Run data_pipeline.py first!")
        self.df = pd.read_csv(self.data_path)

    def predict_recipes(self, user_ingredients_str, dietary_restriction=None, top_n=3):
        """
        Calculates a strict containment/coverage ratio score penalizing 
        missing key ingredients while filtering out minor pantry staples.
        """
        if self.df is None:
            self.load_artifacts()
            
        # Parse user ingredients clean into a set
        user_pantry = set(user_ingredients_str.lower().replace(",", " ").split())
        
        scores = []
        
        for idx, row in self.df.iterrows():
            recipe_ingredients = str(row['cleaned_ingredients']).split()
            
            # Separate the core required ingredients from the basic spices/staples
            core_required = [ing for ing in recipe_ingredients if ing not in self.PANTRY_STAPLES]
            
            if not core_required:
                # Fallback to absolute total count if recipe is purely spices
                core_required = recipe_ingredients
                
            # Count how many core ingredients the user actually has available
            matching_core_count = sum(1 for ing in core_required if ing in user_pantry)
            
            # Score = (Core matching items) / (Total core items required)
            coverage_score = matching_core_count / len(core_required)
            scores.append(coverage_score)

        top_predictions = self.df.copy()
        top_predictions['ml_confidence_score'] = scores
        
        # Apply dietary filter using the category column (set during dataset generation)
        if dietary_restriction and dietary_restriction != "None":
            category_map = {
                "Vegan": "Vegan",
                "Vegetarian": "Vegetarian",
                "Eggitarian": "Eggitarian",
                "Non-Vegetarian": "Non-Vegetarian",
                # Gluten-Free cuts across categories — fallback to name-based list
                "Gluten-Free": None
            }
            mapped = category_map.get(dietary_restriction)
            if mapped:
                if 'dietary_category' in top_predictions.columns:
                    top_predictions = top_predictions[top_predictions['dietary_category'] == mapped]
                # Fallback: if dietary_category column missing, skip filter silently
            elif dietary_restriction == "Gluten-Free":
                gf_dishes = [
                    "South Indian Dosa", "Veggie Stir Fry", "Panner Tikka", "Chicken Fried Rice",
                    "Chana Masala", "French Fries", "Dal Tadka", "Healthy Protein Paneer Tikka",
                    "Nutrient-Dense Oats Porridge", "Baked Salmon with Asparagus", "Moong Dal Khichdi",
                    "Garlic Herb Roasted Chicken", "Chia Seed Vanilla Pudding", "Palak Paneer Light",
                    "Egg White Vegetable Omelet", "Greek Yogurt Fruit Parfait", "Almond Butter Banana Smoothie",
                    "Boiled Egg Salad", "Clear Chicken Broth", "Cucumber Tomato Raita", "Grilled Chicken Salad",
                    "Simple Dal Tadka", "Low-Fat Carrot Halwa", "Spiced Roasted Makhana",
                    "Healthy Egg Bhurji", "Ragi Porridge Malt", "Baked Fish Fillet"
                ]
                # Match base name (strip variation suffix like " (Style v1)")
                top_predictions = top_predictions[
                    top_predictions['name'].str.replace(r' \(Style v\d+\)', '', regex=True).isin(gf_dishes)
                ]
                

        # Sort based on maximum true availability percentage
        top_predictions = top_predictions.sort_values(by='ml_confidence_score', ascending=False)
        top_predictions = top_predictions.head(top_n)
        
        return top_predictions[['name', 'ingredients', 'preparation', 'ml_confidence_score']].to_dict(orient='records')