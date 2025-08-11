import pyttsx3
import speech_recognition as sr
from datetime import date
import datetime
import time
import webbrowser
import sys
import requests
from threading import Thread
import app  # Assuming app.ChatBot is part of your framework
import random
import os
# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()  # Recognizer instance for speech recognition
engine = pyttsx3.init('sapi5')  # Initializing text-to-speech engine
voices = engine.getProperty('voices')  # Getting available voices
engine.setProperty('voice', voices[0].id)  # Setting the voice to use
is_awake = True  # Bot status, determines if the bot is active

# ------------------Functions----------------------
# Reply function for speaking out responses
def reply(audio):
    print(f"echo says: {audio}")  # Logging response to the console
    app.ChatBot.addAppMsg(audio)  # Add message to the chat interface
    engine.say(audio)  # Using pyttsx3 to speak the response
    engine.runAndWait()

# Function to greet the user based on the current time
def wish():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        reply("Good Morning!")
    elif 12 <= hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")
    reply("I am echo, how may I assist you today?")

# Function to capture audio input from the user
def record_audio():
    with sr.Microphone() as source:
        print("Listening...")  # Debug message to indicate that the bot is listening
        r.pause_threshold = 0.8  # Adjusts sensitivity to pauses
        audio = r.listen(source, phrase_time_limit=5)  # Listen for input up to 5 seconds
        try:
            voice_data = r.recognize_google(audio)  # Convert speech to text using Google API
            print(f"Recognized: {voice_data}")  # Debug output to confirm recognition
            app.ChatBot.addUserMsg(voice_data)  # Add user message to the chat interface
        except sr.RequestError:
            reply('Sorry, the service is unavailable. Please check your Internet connection.')
            return ""
        
        except sr.UnknownValueError:
            
            print("Sorry, I did not understand that.")  # Debug message for unrecognized input
            return ""
        return voice_data.lower()  # Convert input to lowercase

# Function to fetch weather information using OpenWeatherMap API
def get_weather(city):
    api_key = os.getenv('WEATHER_API_KEY')  # Replace with your API key
    base_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    response = requests.get(base_url)
    if response.status_code == 200:  # Successful API call
        data = response.json()
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        reply(f"The current weather in {city} is {weather_desc}. The temperature is {temp}°C, and it feels like {feels_like}°C.")
    else:
        reply("Sorry, I couldn't retrieve the weather information. Please check the city name or try again later.")

# Function to tell a joke using an online API
def tell_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:  # Successful response
        joke = response.json()
        reply(joke['setup'] + " ... " + joke['punchline'])
    else:
        reply("Sorry, I couldn't fetch a joke at the moment.")

def get_news():
    response = requests.get(f"https://newsapi.org/v2/everything?q=tesla&from=2024-10-24&sortBy=publishedAt&apiKey={os.getenv('NEWS_API_KEY')}&language=en")
    if response.status_code == 200:  # Successful response
        news = response.json()
        print(len(news["articles"]))
        print(random.randint(0, 99))
        a=random.randint(0, 99)
        reply(news["articles"][a]["title"]+"\n"+news["articles"][a]["description"])
    else:
        reply("Sorry, I couldn't fetch a news at the moment.")


# Function to handle various voice commands
def respond(voice_data):
    global is_awake
    print(voice_data)

    # Check if bot is asleep and reactivate with "wake up"
    if not is_awake:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # Commands when the bot is awake
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply("My name is echo.")

    elif 'date' in voice_data:
        reply(f"Today's date is {today.strftime('%B %d, %Y')}.")

    elif 'time' in voice_data:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        reply(f"The current time is {current_time}.")

    elif 'weather' in voice_data:
        reply("Please tell me the city.")
        city = record_audio()  # Capture the city name
        if city:
            get_weather(city)
    elif 'news' in voice_data:
        get_news()
    elif 'tell me a joke' in voice_data or 'joke' in voice_data:
        tell_joke()

    elif 'search' in voice_data:
        query = voice_data.replace("search", "").strip()

        if query:
            reply(f"Searching for {query}.")
            url = f"https://www.google.com/search?q={query}"
            webbrowser.get().open(url)
            reply("Here is what I found.")
        else:
            reply("I didn't catch what you want to search for.")

    elif 'location' in voice_data:
        reply("Which place are you looking for?")
        place = record_audio()  # Capture the location name
        if place:
            url = f"https://www.google.com/maps/place/{place}"
            webbrowser.get().open(url)
            reply(f"Showing the location of {place} on Google Maps.")

    elif 'bye' in voice_data or 'goodbye' in voice_data:
        reply("Goodbye! Have a great day.")
        is_awake = False
        sys.exit()
    # elif 'exit' in voice_data or 'terminate' in voice_data:
    #     reply("Shutting down. Goodbye!")
    else:
        reply("I'm sorry, I am not programmed to handle that command.")

# ------------------Driver Code--------------------

# Start the chatbot from the app module in a new thread
t1 = Thread(target=app.ChatBot.start)
t1.start()

# Wait for the chatbot to initialize
while not app.ChatBot.started:
    print("Waiting for ChatBot to start...")
    time.sleep(0.5)

# Greet the user when the bot is ready
wish()

# Main loop for continuous interaction
while True:
    voice_data = ""

    # Check if there is user input from the app
    if app.ChatBot.isUserInput():
        voice_data = app.ChatBot.popUserInput()
        print(f"User input received: {voice_data}")

    # If no user input, listen for direct audio input
    if not voice_data:
        voice_data = record_audio()

    # Process the voice command if it contains the activation keyword
    if 'echo' in voice_data:
        try:
            respond(voice_data)
        except SystemExit:
            reply("Exit successful.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break