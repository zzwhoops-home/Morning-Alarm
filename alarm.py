from msilib.schema import Shortcut
import time
import math
from typing import TextIO
from fifteen_api import FifteenAPI
from google.cloud.texttospeech_v1.types.cloud_tts import AudioEncoding, SsmlVoiceGender
from google.cloud import texttospeech
from google_trans_new import google_translator
import os
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from pyowm import OWM
from datetime import datetime

# variables
api_key = ''
lat = 40.3487
lon = -74.659

# initialize text to speech
client = texttospeech.TextToSpeechClient()

# initialize 15ai text to speech
tts_api = FifteenAPI(show_debug=True)

# initialize weather manager
owm = OWM('')
manager = owm.weather_manager()

# get weather data
loc_weather = manager.weather_at_coords(lat, lon)
one_call = manager.one_call(lat=lat, lon=lon, exclude='currently,minutely,hourly', units='standard')
weather = loc_weather.weather

# initialize google translator
translator = google_translator()

# initialize pygame mixer
mixer.init()

# returns the date or time based on input "d" or "t" (output: 'd' --> Friday, March 19, 2021, 't' --> 07:53 PM)
def cur_time(string):
    # get date and time
    x = datetime.now()
    if (string == "d"):
        date = x.strftime("%A, %B %d, %Y")
        return date
    elif (string == "t"):
        time = x.strftime("%I:%M %p")
        return time

# returns the current forecast, 
def forecast():
    forecast = weather.detailed_status
    return f"we're looking at {forecast}"

def wind_speed():
    unit='miles_hour'
    wind = weather.wind(unit=unit)
    speed = round(wind['speed'])
    direction = wind['deg']
    
    if (speed == 0):
        return f"It's still right now."
    elif (speed <= 3):
        return f"It's calm right now. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."
    elif (speed <= 8):
        return f"There's a light breeze outside. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."
    elif (speed <= 15):
        return f"There's a moderate breeze outside. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."
    elif (speed <= 28):
        return f"It's pretty windy outside. Be careful of falling sticks. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."
    elif (speed <= 45):
        return f"There's a gale outside! Exercise caution if traveling outdoors. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."
    elif (speed <= 72):
        return f"I would advise you stay indoors. It's a whole gale outside, and branches and powerlines could break. Stay safe. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."
    elif (speed > 72):
        return f"May God save you. The wind is blowing {degree_to_direction(direction)} at {speed} MPH."


def degree_to_direction(deg):
    num = math.floor(deg / 45)
    cardinal = ['south', 'south-west', 'west', 'north-west', 'north', 'north-east', 'east', 'south-east']
    return cardinal[num]

# returns the current temperature, along with how cold or warm it is.
def temp(unit):
    cur_temp_dict = weather.temperature(unit)
    forecast_temp_dict = one_call.forecast_daily[0].temperature(unit)

    cur_temp = round(cur_temp_dict['temp'])
    max_temp = round(forecast_temp_dict['max'])
    min_temp = round(forecast_temp_dict['min'])
    feels_like = round(cur_temp_dict['feels_like'])
    difference = cur_temp - feels_like

    if (unit == 'fahrenheit'):
        unit_symbol = "°F"
    elif (unit == 'celsius'):
        unit_symbol = "°C"
    elif (unit == 'kelvin'):
        unit_symbol = "U nerd"

    def temp_forecast():
        return f"Right now, it's {cur_temp}{unit_symbol}, but feels like {feels_like}. We're looking at a forecasted high of {max_temp} and low of {min_temp}"

    text = ""

    if (cur_temp <= -40):
        text += f"Keep your hazard protection charged. {temp_forecast()}. "
    elif (cur_temp <= 0):
        text = f"It's freezing outside. {temp_forecast()}. You should probably stay inside. "
    elif (cur_temp <= 25):
        text = f"It's very cold outside today. {temp_forecast()}. I think I'd prefer... to stay inside "
    elif (cur_temp <= 40):
        text = f"It's cold outside today. {temp_forecast()}. Make sure you bring a jacket, hat, and gloves! "
    elif (cur_temp <= 55):
        text = f"It's chilly outside today! {temp_forecast()}. Bring a jacket... or don't. "
    elif (cur_temp <= 75):
        text = f"It's rather comfortable outside today. {temp_forecast()}. "
    elif (cur_temp <= 85):
        text = f"It's going to be a warm day! {temp_forecast()}. "
    elif (cur_temp <= 93):
        text = f"Today's going to be hot! {temp_forecast()}. Make sure to bring a water bottle with you. "
    elif (cur_temp <= 99):
        text = f"It's very hot outside! {temp_forecast()}. Remember to stay hydrated, or, well, good luck. "
    elif (cur_temp > 100):
        text = f"It's scorching outside! You don't see three numbers in the temperature very often. {temp_forecast()}. Stay indoors today. There's no AC outdoors. "

    return(text)

# combines all functions together to return a morning report.
def text():
    return f"Hello, Zachary. It is currently {cur_time('t')} on {cur_time('d')}, and {forecast()}. {temp('fahrenheit')} {wind_speed()}"

#text = translator.translate(text(), lang_src='en', lang_tgt='en')
#print(text)

# using google cloud natural text to speech, calling the text() function for what text to speak. Then, set the voice and config the audio, and save to a mp3 file

"""
synthesis_input = texttospeech.SynthesisInput(text=text())
voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Wavenet-D")
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, pitch=0, speaking_rate=1)
response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

with open("alarm.mp3", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "alarm.mp3"')
"""

text = text()
first_part = text[:len(text)//10]

tts_api.save_to_file("GLaDOS", "Hello, Zachary. It is currently Eight forty-one PM on Tuesday, March first, twenty twenty two, and we're looking at scattered clouds. It's chilly outside today! Right now, it's forty four degrees.", "alarm.wav")


# get sound length to find amount of time to suspend program execution (may replace with asyncio)
sound = WAVE("alarm.wav")
sound_length = sound.info.length

# load alarm.mp3 and then play the file.
sound_obj = mixer.Sound("alarm.wav")
sound_obj.play()

# suspend program execution until the morning report has finished. Useful if multiple sound files will be played to satisfy character limits with API calls.
time.sleep(sound_length)

print(text())