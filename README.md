# 🍳 NutriChef AI — Personalized Daily Meal Planner

> Turn your fridge ingredients into a full-day healthy meal plan, powered by local Llama 3.2 + ML recipe matching.

---

## 🧠 How It Works

```
User inputs (age, weight, height, ingredients)
        ↓
ML Recommender (KNN + TF-IDF ingredient coverage scoring)
        ↓
Llama 3.2 via Ollama (generates 3-meal plan as JSON)
        ↓
Streamlit UI (displays macros, swap button, shopping list)
        ↓
Daily Scheduler (emails plan at 6:00 AM via Gmail SMTP)
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your Gmail credentials
```

### 3. Install and start Ollama
```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2:3b
```

### 4. Generate the recipe dataset
```bash
python generate_dataset.py
python data_pipeline.py
```

### 5. Start the FastAPI backend
```bash
uvicorn app:app --reload
```

### 6. Launch the Streamlit frontend
```bash
streamlit run streamlit_app.py
```

### 7. (Optional) Start the daily email scheduler
```bash
python daily_scheduler.py
```

---

## 📁 Project Structure

```
NutriChef_AI/
├── app.py                  # FastAPI backend (LLM + ML layer)
├── streamlit_app.py        # Streamlit frontend UI
├── recommender.py          # ML ingredient-matching engine
├── preferences.py          # User feedback & adaptive learning
├── generate_dataset.py     # Builds 200-recipe dataset
├── data_pipeline.py        # Cleans & prepares data for ML
├── daily_scheduler.py      # Email scheduler (6 AM daily)
├── requirements.txt        # Pinned dependencies
├── .env.example            # Credential template (never commit .env)
└── data/
    ├── raw_recipes.csv
    ├── cleaned_recipes.csv
    └── user_preferences.json
```

---

## ✨ Features

- **3-meal daily plan** — breakfast, lunch, dinner tailored to your pantry
- **Dietary filters** — Vegetarian, Vegan, Eggitarian, Non-Veg, Gluten-Free
- **BMR-aware calorie targeting** — uses Mifflin-St Jeor formula
- **ML ingredient matching** — coverage scoring pre-filters recipes before LLM call
- **Adaptive feedback loop** — rate meals → preferences influence future plans
- **Swap button** — regenerate any single meal slot without redoing the full plan
- **Shopping list export** — download missing ingredients as `.txt`
- **Daily email digest** — automated HTML email at 6:00 AM

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recommend` | Generate full-day meal plan |
| POST | `/feedback` | Submit meal rating (1–5) |

### Example `/recommend` payload
```json
{
  "user_name": "Navya",
  "age": 31,
  "weight": 63.0,
  "height": 165.0,
  "ingredients": "Rice, Eggs, Spinach, Onions, Tomatoes",
  "dietary_restriction": "Vegetarian",
  "health_goal": "Maintenance"
}
```

---

## 🔒 Security Note

Never commit your `.env` file. Add it to `.gitignore`:
```
.env
data/user_preferences.json
```

---

## 🛠️ Tech Stack

`FastAPI` · `Streamlit` · `Ollama (Llama 3.2)` · `scikit-learn` · `pandas` · `schedule` · `python-dotenv`

---

## 👩‍💻 Author

**Navya** — AI/ML Engineering Student, Masai School 2025–26
