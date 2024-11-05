import streamlit as st
import pandas as pd
import requests
import random
from data import food_items_breakfast, food_items_lunch, food_items_dinner
from prompts import pre_prompt_b, pre_prompt_l, pre_prompt_d, pre_breakfast, pre_lunch, pre_dinner, end_text, \
    example_response_l, example_response_d, negative_prompt

# Constants
UNITS_CM_TO_IN = 0.393701
UNITS_KG_TO_LB = 2.20462
UNITS_LB_TO_KG = 0.453592
UNITS_IN_TO_CM = 2.54

HUGGINGFACE_API_KEY = st.secrets["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"]
model_id = "meta-llama/Meta-Llama-3-70B-Instruct"

st.set_page_config(page_title="AI - Meal Planner", page_icon="🍴")
st.title("AI Meal Planner")
st.divider()
st.write(
    "This is an AI-based meal planner that uses a person's information to create a personalized meal plan."
    " The planner can be used to find a meal plan that satisfies the user's calorie and macronutrient requirements."
)
st.markdown("*Powered by Hugging Face’s Llama-3 70B*")
st.divider()

# Input user details
st.write("Enter your information:")
name = st.text_input("Enter your name")
age = st.number_input("Enter your age", step=1)
unit_preference = st.radio("Preferred units:", ["Metric (kg, cm)", "Imperial (lb, ft + in)"])

if unit_preference == "Metric (kg, cm)":
    weight = st.number_input("Enter your weight (kg)")
    height = st.number_input("Enter your height (cm)")
else:
    weight_lb = st.number_input("Enter your weight (lb)")
    col1, col2 = st.columns(2)
    with col1:
        height_ft = st.number_input("Enter your height (ft)")
    with col2:
        height_in = st.number_input("Enter your height (in)")
    weight = weight_lb * UNITS_LB_TO_KG
    height = (height_ft * 12 + height_in) * UNITS_IN_TO_CM

gender = st.radio("Choose your gender:", ["Male", "Female"])

# Example response
example_response = f"Hello {name}! I'm thrilled to be your meal planner for the day..."

# Function to calculate BMR
def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        bmr = 9.99 * weight + 6.25 * height - 4.92 * age + 5
    else:
        bmr = 9.99 * weight + 6.25 * height - 4.92 * age - 161
    return bmr

# Function to generate items list for target calories
def generate_items_list(target_calories, food_groups):
    calories = 0
    selected_items = []
    total_items = set()
    for foods in food_groups.values():
        total_items.update(foods.keys())
    while abs(calories - target_calories) >= 10 and len(selected_items) < len(total_items):
        group = random.choice(list(food_groups.keys()))
        foods = food_groups[group]
        item = random.choice(list(foods.keys()))
        if item not in selected_items:
            cals = foods[item]
            if calories + cals <= target_calories:
                selected_items.append(item)
                calories += cals
    return selected_items, calories

# Knapsack algorithm for calorie matching
def knapsack(target_calories, food_groups):
    items = []
    for group, foods in food_groups.items():
        for item, calories in foods.items():
            items.append((calories, item))
    n = len(items)
    dp = [[0 for _ in range(target_calories + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(target_calories + 1):
            value, _ = items[i - 1]
            if value > j:
                dp[i][j] = dp[i - 1][j]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - value] + value)
    selected_items = []
    j = target_calories
    for i in range(n, 0, -1):
        if dp[i][j] != dp[i - 1][j]:
            _, item = items[i - 1]
            selected_items.append(item)
            j -= items[i - 1][0]
    return selected_items, dp[n][target_calories]

# Calculate BMR and display
bmr = calculate_bmr(weight, height, age, gender)
round_bmr = round(bmr, 2)
st.subheader(f"Your daily intake needs to have: {round_bmr} calories")
choose_algo = "Knapsack"

# Click to create basket
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button("Create a Basket", on_click=click_button)
if st.session_state.clicked:
    calories_breakfast = round((bmr * 0.5), 2)
    calories_lunch = round((bmr * (1 / 3)), 2)
    calories_dinner = round((bmr * (1 / 6)), 2)
    if choose_algo == "Random Greedy":
        meal_items_morning, cal_m = generate_items_list(calories_breakfast, food_items_breakfast)
        meal_items_lunch, cal_l = generate_items_list(calories_lunch, food_items_lunch)
        meal_items_dinner, cal_d = generate_items_list(calories_dinner, food_items_dinner)
    else:
        meal_items_morning, cal_m = knapsack(int(calories_breakfast), food_items_breakfast)
        meal_items_lunch, cal_l = knapsack(int(calories_lunch), food_items_lunch)
        meal_items_dinner, cal_d = knapsack(int(calories_dinner), food_items_dinner)

    st.header("Your Personalized Meal Plan")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Calories for Morning: " + str(calories_breakfast))
        st.dataframe(pd.DataFrame({"Morning": meal_items_morning}))
        st.write("Total Calories: " + str(cal_m))

    with col2:
        st.write("Calories for Lunch: " + str(calories_lunch))
        st.dataframe(pd.DataFrame({"Lunch": meal_items_lunch}))
        st.write("Total Calories: " + str(cal_l))

    with col3:
        st.write("Calories for Dinner: " + str(calories_dinner))
        st.dataframe(pd.DataFrame({"Dinner": meal_items_dinner}))
        st.write("Total Calories: " + str(cal_d))

    if st.button("Generate Meal Plan"):
        st.markdown("---")
        
        for meal, meal_items, calorie_goal, prompt in zip(
            ["Breakfast", "Lunch", "Dinner"],
            [meal_items_morning, meal_items_lunch, meal_items_dinner],
            [calories_breakfast, calories_lunch, calories_dinner],
            [pre_prompt_b, pre_prompt_l, pre_prompt_d]
        ):
            st.subheader(meal)
            user_content = f"{prompt} {meal_items} {example_response}"
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers={"Authorization": f"Bearer {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}"},
                json={"inputs": user_content}
            )
            if response.status_code == 200:
                full_response = response.json()[0]["generated_text"]
                st.write(full_response)
            else:
                st.error("Error in generating meal plan.")
                
        st.write("Thank you for using our AI app! Enjoy your meal plan!")
        
# Hide Streamlit footer and menu
hide_streamlit_style = """
                    <style>
                    # MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
