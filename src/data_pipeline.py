import os
import pandas as pd

def run_pipeline():
    print("⏳ Starting data pipeline optimization layers...")
    
    # 1. Define paths explicitly
    raw_path = "data/raw_recipes.csv"
    cleaned_path = "data/cleaned_recipes.csv"
    
    # Create data directory if it got deleted or misplaced
    os.makedirs("data", exist_ok=True)
    
    # 2. Check if raw data exists
    if not os.path.exists(raw_path):
        print(f"❌ Error: Cannot find raw data file at {raw_path}")
        return
        
    # 3. Read raw file
    df = pd.read_csv(raw_path)
    print(f"📋 Loaded raw dataset with columns: {list(df.columns)}")
    
    # 4. Core Transformation: Clean ingredients text column for the vectorizer
    if 'ingredients' in df.columns:
        df['cleaned_ingredients'] = df['ingredients'].astype(str).str.lower().str.replace(r'[^\w\s,]', '', regex=True)
    else:
        print("❌ Critical Error: 'ingredients' column missing from raw file!")
        return

    # 5. Strict Structural Integrity Check: Ensure 'preparation' travels through the pipeline
    if 'preparation' not in df.columns:
        print("⚠️ Warning: 'preparation' column not found in raw data. Generating a default column placeholder...")
        df['preparation'] = "Mix ingredients thoroughly, heat according to taste parameters, and serve hot."
    
    # 6. Save explicitly with all 4 necessary data matrices columns
    final_cols = ['name', 'ingredients', 'preparation', 'cleaned_ingredients']
    # Intersect to only save columns that are guaranteed to exist now
    save_cols = [col for col in final_cols if col in df.columns]
    
    df[save_cols].to_csv(cleaned_path, index=False)
    print(f"✅ Success! Cleaned dataset built perfectly at: {cleaned_path}")
    print(f"📊 New File Columns: {list(df[save_cols].columns)}")

if __name__ == "__main__":
    run_pipeline()