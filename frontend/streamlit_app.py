import streamlit as st
import requests

# 1. Page Configuration & Custom Theme Setting
st.set_page_config(
    page_title="NutriChef AI | Full-Day Menu Planner",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium UI style sheet configurations
st.markdown("""
    <style>
    .main-title { font-size: 2.6rem !important; font-weight: 700 !important; color: #1E3A8A; margin-bottom: 0.2rem; }
    .subtitle { font-size: 1.1rem !important; color: #4B5563; margin-bottom: 2rem; }
    .meal-header { font-size: 1.4rem !important; font-weight: 600 !important; color: #10B981; margin-top: 1rem; }
    .timeline-card { background-color: #FAFAFA; border: 1px solid #E5E7EB; padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .badge { background-color: #E0F2FE; color: #0369A1; padding: 0.2rem 0.6rem; border-radius: 0.25rem; font-size: 0.85rem; font-weight: 500; }
    
    /* 🌟 NEW: Premium Metric Dashboard Card Style Sheet */
    .metric-card { background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 2rem; }
    .metric-title { font-size: 0.9rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9; }
    .metric-value { font-size: 2rem !important; font-weight: 700 !important; margin-top: 0.2rem; }
    </style>
""", unsafe_allow_html=True)

# High-Speed Caching Function Optimization for Full Generation
@st.cache_data(show_spinner=False)
def fetch_recipe_plan(payload_dict):
    response = requests.post("http://127.0.0.1:8000/recommend", json=payload_dict)
    return response.json()

# Single-Slot Live Hot-Swapping Network Routine
def quick_swap_slot(payload_dict, slot_key):
    payload_dict["target_slot"] = slot_key
    try:
        response = requests.post("http://127.0.0.1:8000/recommend", json=payload_dict)
        r_data = response.json()
        if r_data.get("success"):
            new_meal = r_data["full_day_plan"].get(slot_key)
            if new_meal:
                st.session_state.generated_plan[slot_key] = new_meal
                st.toast(f"🔄 Swapped out your {slot_key} meal layout with a fresh variation!")
    except Exception as e:
        st.error(f"Failed to quick-swap selection: {str(e)}")

# Initialize Session State values to persist memory across tab clicks
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = None
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "current_payload" not in st.session_state:
    st.session_state.current_payload = None

# 2. Sidebar Panel Layout
with st.sidebar:
    st.markdown("### 🛠️ Configuration Controls")
    st.caption("Use the tabs on the main screen canvas to input your current health goals and kitchen metrics.")

# 3. Main Analytics Screen Layout Onboarding Wizard
st.markdown('<div class="main-title">🍳 NutriChef AI Automated Diet Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart, zero-waste meal planning. Turn the ingredients in your fridge into a personalized, healthy menu for the entire day.</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["👤 1. Health Biomarkers", "🛒 2. Kitchen Pantry", "📋 3. Your Menu Plan"])

with tab1:
    st.subheader("Step 1: Tell us about your health baseline")
    name_input = st.text_input("User Name:", value="", placeholder="Type your name here...")
    
    c_age, c_wt = st.columns(2)
    with c_age: 
        age_input = st.number_input("Age (Years):", min_value=1, max_value=120, value=None, placeholder="e.g. 31")
    with c_wt: 
        weight_input = st.number_input("Weight (Kg):", min_value=10.0, max_value=250.0, value=None, placeholder="e.g. 63.0")
        
    goal_option = st.selectbox("Primary Health & Nutrition Goal:", ["Maintenance", "Weight Loss", "Muscle Gain", "Diabetic-Friendly"], key="health_goal_unique")

with tab2:
    st.subheader("Step 2: Check your ingredient pantry and select what you have available")
    
    # 🌟 FIX 1: Typo-Safe Tag/Chip Input Autocomplete Dropdown
    INGREDIENT_LIBRARY = sorted([
        "Rice", "Urad Dal", "Wheat Flour", "Chicken", "Eggs", "Spinach", "Paneer", "Oats", 
        "Tomatoes", "Onions", "Milk", "Curd", "Potatoes", "Carrots", "Garlic", "Ginger", 
        "Coriander", "Green Chiles", "Lemon", "Butter", "Cheese", "Cashews", "Fish","Toor Dal","Beans", "Drumsticks",
        "Cabbage", "Coconut", "Bell Peppers", "Mushrooms", "Broccoli", "Cauliflower", "Chickpeas"
    ])
    
    selected_tags = st.multiselect(
        "Select Available Ingredients in House:",
        options=INGREDIENT_LIBRARY,
        placeholder="Type to search and add kitchen items (e.g., Spinach, Eggs)...",
        key="pantry_chips_unique"
    )
    
    # Clean and consolidate selection into a format compatible with the backend script
    user_ingredients_string = ", ".join(selected_tags)
    
    diet_option = st.selectbox("Dietary Restrictions:", ["None", "Vegetarian", "Non-Vegetarian", "Eggitarian", "vegan", "Gluten-Free"], key="diet_selection_unique")
    
    st.markdown("---")
    generate_btn = st.button("🔮 Generate Full-Day Menu Plan", use_container_width=True)

    if generate_btn:
        if not name_input or age_input is None or weight_input is None:
            st.error("⚠️ Form Incomplete! Please enter your Name, Age, and Weight in Step 1 first.")
        elif not selected_tags:
            st.error("⚠️ Pantry Empty! Please select at least one available ingredient in Step 2 first.")
        else:
            with st.spinner("🍳 Our AI Chef is crafting your custom meal plan and calculating your nutrition numbers..."):
                payload = {
                    "user_name": str(name_input).strip().title(),  # Auto-capitalize names cleanly
                    "age": int(age_input),
                    "weight": float(weight_input),
                    "ingredients": str(user_ingredients_string),
                    "dietary_restriction": None if diet_option == "None" else str(diet_option),
                    "health_goal": str(goal_option),
                    "target_slot": "all"
                }
                try:
                    response_data = fetch_recipe_plan(payload)
                    if response_data.get("success"):
                        st.session_state.metadata = response_data.get("user_metadata", {})
                        st.session_state.generated_plan = response_data.get("full_day_plan", {})
                        st.session_state.current_payload = payload
                        st.success("🎉 Plan successfully generated! Please click on '📋 3. Your Menu Plan' tab above to view your meals.")
                    else:
                        st.error("❌ The backend system failed to allocate recipes safely.")
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Connection Refused! Check your backend server.")

with tab3:
    if st.session_state.generated_plan is None:
        st.info("💡 **Ready to Plan Your Day?** Simply fill out your health details in Step 1, select your ingredients in Step 2, and hit generate!")
    else:
        metadata = st.session_state.metadata
        plan = st.session_state.generated_plan
        
        # 🌟 FIX 3: Premium Dynamic Target Summary Banner Card
        target_cal_display = metadata.get('target_calories', 'Calculated Baseline')
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🎯 Caloric Budget Profile Blueprint</div>
                <div class="metric-value">{target_cal_display}</div>
            </div>
        """, unsafe_allow_html=True)
        
        meal_slots = [
            {"title": "🌅 Morning Breakfast Slot", "key": "morning", "color": "#F59E0B"},
            {"title": "☀️ Afternoon Lunch Slot", "key": "afternoon", "color": "#10B981"},
            {"title": "🌙 Evening Snack & Dinner Slot", "key": "evening", "color": "#6366F1"}
        ]
        
        PANTRY_STAPLES = {'water', 'salt', 'oil', 'ghee', 'turmeric', 'chillis', 'chilli powder', 'garam masala', 'cumin', 'ginger garlic paste', 'black pepper', 'coriander leaves'}
        master_missing_accumulator = []

        for slot in meal_slots:
            meal_data = plan.get(slot['key'])
            if meal_data:
                meal_name = meal_data.get('name', 'Healthy Meal Choice')
                
                # Header Split Column Grid layout wrapper block to anchor local buttons beautifully
                head_col, action_col = st.columns([5, 1])
                with head_col:
                    st.markdown(f"""
                        <div class="timeline-card" style="border-left: 6px solid {slot['color']}; margin-bottom: 0rem; padding: 0.8rem 1.2rem;">
                            <span class="badge" style="background-color: {slot['color']}22; color: {slot['color']};">{slot['title'].upper()}</span>
                            <h3 style="margin-top: 0.4rem; margin-bottom: 0rem;">{meal_name.title()}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                with action_col:
                    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                    if st.button(f"🔄 Swap", key=f"quick_swap_btn_{slot['key']}", use_container_width=True):
                        with st.spinner("Swapping meal..."):
                            quick_swap_slot(st.session_state.current_payload, slot['key'])
                            st.rerun()

                # Nutrient Breakdown Grid System Metrics
                macro_col1, macro_col2, macro_col3, macro_col4 = st.columns(4)
                macro_col1.metric("🔥 Energy", f"{meal_data.get('calories', 'N/A')} kcal")
                macro_col2.metric("🥩 Protein", meal_data.get('protein', 'N/A'))
                macro_col3.metric("🍞 Carbs", meal_data.get('carbs', 'N/A'))
                macro_col4.metric("🥑 Fats", meal_data.get('fats', 'N/A'))
                
                txt_col, score_col = st.columns([5, 1])
                with txt_col:
                    pantry_tokens = set([i.strip().lower() for i in user_ingredients_string.replace(",", " ").split()])
                    raw_ingredients = meal_data.get('ingredients', '')
                    recipe_tokens = [str(item).lower() for item in raw_ingredients] if isinstance(raw_ingredients, list) else str(raw_ingredients).lower().split()

                    owned_items = []
                    missing_items = []

                    for item in recipe_tokens:
                        if item in pantry_tokens:
                            owned_items.append(f"`{item.title()}`")  # Auto-capitalize list items cleanly
                        elif item in PANTRY_STAPLES:
                            owned_items.append(f"`{item.title()} (staple)`")
                        else:
                            missing_items.append(f"`{item.title()}`")
                            master_missing_accumulator.append(item)

                    st.write(f"🍏 **Available in Your Fridge:** {', '.join(owned_items) if owned_items else 'None'}")
                    if missing_items:
                        st.write(f"🛒 **Missing Ingredients Needed:** {', '.join(missing_items)}")

                with score_col:
                    match_score = round(meal_data.get('ml_confidence_score', 0.85) * 100, 1)
                    st.metric("Inventory Match", f"{match_score}%")
                    
                with st.expander("📖 View Cooking Instructions & Preparation"):
                    # 🌟 FIX 2: Parse Raw Arrays/Strings and Format into Clean Numbered Markdown Steps
                    raw_prep = meal_data.get('preparation', '')
                    
                    if isinstance(raw_prep, list):
                        steps_list = raw_prep
                    elif isinstance(raw_prep, str):
                        # Clean bracket artifacts if model returned string-serialized arrays
                        clean_prep = raw_prep.strip("[]'\"")
                        steps_list = [step.strip("'\" ") for step in clean_prep.split("', '") if step]
                    else:
                        steps_list = ["Prepare core elements and mix thoroughly."]
                        
                    # Render step text elements beautifully using native markdown list tokens
                    for idx, step in enumerate(steps_list, start=1):
                        st.markdown(f"**{idx}.** {step}")
                
                st.markdown("<br>", unsafe_allow_html=True)
        
        if master_missing_accumulator:
            st.markdown("---")
            st.markdown("### 🧺 Master Shopping Checklist")
            unique_missing = sorted(list(set(master_missing_accumulator)))
            shopping_text = "NUTRICHEF AI GROCERY LIST\n=========================\n\n"
            for item in unique_missing:
                shopping_text += f"[ ] Buy: {item.title()}\n"

            st.download_button(label="📥 Export Missing Ingredients to File", data=shopping_text, file_name="nutrichef_shopping_list.txt", mime="text/plain", use_container_width=True)