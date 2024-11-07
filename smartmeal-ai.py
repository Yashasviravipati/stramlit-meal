import streamlit as st

# Define a function to calculate daily calorie intake
def calculate_calories(age, weight, height, gender):
    if gender == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    # Assuming moderate activity level (maintenance level)
    daily_calories = bmr * 1.55
    return daily_calories

# Streamlit application
st.title("Daily Calorie Intake Calculator")

# Input fields
name = st.text_input("Name")
age = st.number_input("Age", min_value=1, max_value=120, step=1)
weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, step=0.1)
height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, step=0.1)
gender = st.selectbox("Gender", ["Male", "Female"])

# Calculate button
if st.button("Calculate"):
    if name and age and weight and height and gender:
        daily_calories = calculate_calories(age, weight, height, gender)
        st.success(f"Hello {name}! Based on your inputs, your daily caloric requirement is approximately {daily_calories:.2f} calories.")
    else:
        st.error("Please fill in all fields.")
