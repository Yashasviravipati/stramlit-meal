import streamlit as st
import requests

# Hugging Face API information
API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": "Bearer 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"}

# Function to get meal plan with descriptions from Hugging Face
def get_meal_plan_with_descriptions(calories, restrictions):
    prompt = (f"Generate a meal plan for a whole day with approximately {calories} calories. "
              f"Each meal should come with a brief description. Dietary restrictions: {', '.join(restrictions)}.")
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.ok:
        meal_plan = response.json()[0]["generated_text"]
    else:
        meal_plan = "Meal plan could not be generated."
    return meal_plan

# Calorie calculation function
def calculate_calories(age, weight, height, gender):
    if gender == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    daily_calories = bmr * 1.55  # Assuming moderate activity level
    return daily_calories

# Streamlit application
st.title("Daily Calorie Intake & Meal Plan with Descriptions")

# Input fields
name = st.text_input("Name")
age = st.number_input("Age", min_value=1, max_value=120, step=1)
weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, step=0.1)
height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, step=0.1)
gender = st.selectbox("Gender", ["Male", "Female"])
restrictions = st.multiselect("Dietary Restrictions", ["Diabetic", "Vegan", "Vegetarian", "Gluten-Free", "Lactose-Free", "Low-Carb"])

# Calculate button
if st.button("Calculate & Get Meal Plan"):
    if name and age and weight and height and gender:
        daily_calories = calculate_calories(age, weight, height, gender)
        meal_plan = get_meal_plan_with_descriptions(daily_calories, restrictions)
        st.success(f"Hello {name}! Your daily caloric requirement is approximately {daily_calories:.2f} calories.")
        st.subheader("Suggested Meal Plan with Descriptions:")
        st.write(meal_plan)
    else:
        st.error("Please fill in all fields.")
