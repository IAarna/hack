from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import openai
import requests
import os

app = FastAPI()

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
openai.api_key = OPENAI_API_KEY

class DietPlanRequest(BaseModel):
    age: int
    sex: str
    weight: float
    height: int
    diet_preference: str
    health_goal: str
    activity_level: str
    city: str

# Function to get weather information
def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return f"{description.capitalize()}, {temp}°C"
    else:
        return None

# Function to generate diet plan
def generate_diet_plan(age, sex, weight, height, diet_preference, health_goal, activity_level, weather, city):
    prompt = f"""
    Create a personalized diet plan based on the following details:
    - Age: {age} years
    - Sex: {sex}
    - Weight: {weight} kg
    - Height: {height} cm
    - Dietary Preferences: {diet_preference}
    - Health Goals: {health_goal}
    - Activity Level: {activity_level}
    - Weather: {weather}
    - Location: {city}

    The diet plan should include:
    1. A daily meal plan (breakfast, lunch, dinner, snacks).
    2. Portion sizes (considering the user's weight, height, and activity level).
    3. A variety of foods within the given dietary preference.
    4. Nutritional tips based on the weather (e.g., hydrating in hot weather, warming foods in cold weather).
    5. Suggestions for meals that help with the user's health goal (e.g., weight loss, maintenance, or muscle gain).
    6. An emphasis on nutrient balance (protein, carbs, fats, vitamins, minerals).
    7. Include foods that are easy to prepare and accessible.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300
    )
    return response['choices'][0]['message']['content'].strip()

@app.post("/generate_diet_plan")
def create_diet_plan(request: DietPlanRequest):
    weather = get_weather(request.city)
    if not weather:
        raise HTTPException(status_code=404, detail="Could not fetch weather data for the provided city.")
    
    diet_plan = generate_diet_plan(
        age=request.age,
        sex=request.sex,
        weight=request.weight,
        height=request.height,
        diet_preference=request.diet_preference,
        health_goal=request.health_goal,
        activity_level=request.activity_level,
        weather=weather,
        city=request.city
    )
    return {"diet_plan": diet_plan}

