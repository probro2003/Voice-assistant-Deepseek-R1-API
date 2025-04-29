import speech_recognition as sr
import pyttsx3
import datetime
from googlesearch import search
import webbrowser
import os
import random
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import subprocess
import numpy as np
import keyboard
from openai import OpenAI
from dotenv import load_dotenv
import os
import threading  


# Load the .env file
load_dotenv()

# Access your API key stored in the .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenAI (for OpenRouter)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def deepseek_chat(user_query):
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "user", "content": user_query}
            ]
        )
        answer = completion.choices[0].message.content
        return answer.strip()
    except Exception as e:
        print(f"DeepSeek API Error: {e}")
        return "Sorry, I couldn't fetch a response right now."

    
# Initialize audio control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)

# Global flag for skipping speech and exiting program
skip_speech = False
exit_program = False

def speak(text):
    global skip_speech

    def monitor_keyboard():
        global skip_speech
        # Wait for a specific key to be pressed (e.g., Spacebar)
        while engine.isBusy():
            if keyboard.is_pressed('space'):
                skip_speech = True
                engine.stop()
                print("Speech interrupted!")
                break

    print(f"MANA: {text}")
    engine.say(text)
    skip_speech = False

    # Start a background thread to monitor keyboard
    threading.Thread(target=monitor_keyboard, daemon=True).start()

    engine.runAndWait()



# System Control Functions
def set_brightness(level):
    try:
        sbc.set_brightness(level)
        speak(f"Brightness set to {level}%")
    except Exception as e:
        speak("Could not adjust brightness")

def adjust_brightness(delta=10):
    current = sbc.get_brightness()[0]
    new_level = max(0, min(100, current + delta))
    set_brightness(new_level)

def set_volume(level):
    try:
        vol_scale = np.interp(level, [0, 100], [min_vol, max_vol])
        volume.SetMasterVolumeLevel(vol_scale, None)
        speak(f"Volume set to {level}%")
    except Exception as e:
        speak("Could not adjust volume")

def adjust_volume(delta=10):
    current = np.interp(volume.GetMasterVolumeLevel(), [min_vol, max_vol], [0, 100])
    new_level = max(0, min(100, current + delta))
    set_volume(new_level)

# def toggle_wifi(state):
#     try:
#         cmd = 'enable' if state else 'disable'
#         subprocess.run(f'netsh interface set interface "Wi-Fi" {cmd}', shell=True, check=True)
#         speak(f"Wi-Fi {cmd}d")
#     except Exception as e:
#         speak("Failed to modify Wi-Fi settings. Run as administrator?")

def toggle_hotspot(state):
    try:
        action = 'start' if state else 'stop'
        subprocess.run(f'netsh wlan {action} hostednetwork', shell=True, check=True)
        speak(f"Mobile hotspot {action}ed")
    except Exception as e:
        speak("Hotspot control failed. Check administrator privileges.")

# def toggle_airplane_mode(state):
#     try:
#         path = r"SYSTEM\CurrentControlSet\Control\RadioManagement\SystemRadioState"
#         with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_WRITE) as key:
#             winreg.SetValueEx(key, '', 0, winreg.REG_DWORD, 1 if state else 0)
#         speak("Airplane mode " + ("enabled" if state else "disabled"))
#     except Exception as e:
#         speak("Failed to modify airplane mode. Administrator rights required.")

def toggle_battery_saver(state):
    try:
        if state:
            # Activate Battery Saver
            subprocess.run('powercfg /setactive SCHEME_MIN', shell=True, check=True)
            speak("Switched to Balanced mode")
        else:
            # Revert to Balanced plan
            subprocess.run('powercfg /setactive SCHEME_BALANCED', shell=True, check=True)
            speak("Battery Saver activated")
    except subprocess.CalledProcessError as e:
        speak("Failed to change power plan. Run as administrator?")

def toggle_night_light(state):
    try:
        cmd = 'enable' if state else 'disable'
        subprocess.run(f'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate" /v Data /t REG_BINARY /d feffffff01000000 /f' if state else 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate" /f', shell=True)
        subprocess.run('taskkill /f /im SearchHost.exe', shell=True)
        speak(f"Night light {cmd}d")
    except Exception as e:
        speak("Night light control failed")

# Function to greet user
def wish_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am MANA, your virtual assistant. How can I help you today?")

# Voice recognition function
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        return query.lower()
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I didn't catch that. Can you please repeat?")
        return "None"

# Google Search implementation
def google_search(query, num_results=5):
    try:
        search_results = []
        for url in search(query, num_results=num_results):
            search_results.append(url)
        return search_results
    except Exception as e:
        print(f"Google Search Error: {e}")
        return []

# Function to get yesterday's date
def get_yesterday_date():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    return yesterday.strftime("%B %d, %Y")

# Function to get tomorrow's date
def get_tomorrow_date():
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    return tomorrow.strftime("%B %d, %Y")


# Main command processor
def process_command(query):
    now = datetime.datetime.now()
    global exit_program 

    # Recognize MANA's name
    if 'hello' in query:
       speak("Yes, I'm here! How can I assist you?")
    
    # Google Search – open the top result directly
    elif 'search' in query: # or 'google' in query:
        search_query = query.replace("search", "").strip()
        if search_query:
            speak(f"Searching Google for {search_query}")
            results = google_search(search_query)
            if results:
                speak("Opening the top result.")
                webbrowser.open(results[0])
            else:
                speak("No results found for your query")
    
        else:
            speak("Please specify what you want to search for")

    
     # System Controls
    elif 'brightness' in query:
        if 'increase' in query:
            adjust_brightness(20)
        elif 'decrease' in query:
            adjust_brightness(-20)
        elif 'maximum' in query:
            set_brightness(100)
        elif 'minimum' in query:
            set_brightness(0)
            
    elif 'volume' in query:
        if 'mute' in query or 'unmute' in query:
            volume.SetMute(1 if 'mute' in query else 0, None)
            speak("Volume muted" if 'mute' in query else "Volume unmuted")
        elif 'increase' in query:
            adjust_volume(10)
        elif 'decrease' in query:
            adjust_volume(-10)
        elif 'maximum' in query:
            set_volume(100)
        elif 'minimum' in query:
            set_volume(0)
            
    # elif 'wifi' in query:
    #     toggle_wifi('enable' in query or 'on' in query)
        
    elif 'hotspot' in query:
        toggle_hotspot('enable' in query or 'on' in query)
        
    # elif 'airplane mode' in query:
    #     toggle_airplane_mode('enable' in query or 'on' in query)
        
    elif 'battery saver' in query:
        toggle_battery_saver('enable' in query or 'on' in query)
        
    elif 'night light' in query:
        toggle_night_light('enable' in query or 'on' in query)

    # Time information
    elif 'time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {strTime}")
    
     # Date queries
    elif 'date' in query:
        if 'date before yesterday' in query:
            target_date = now - datetime.timedelta(days=2)
            response = target_date.strftime("The date for the day before yesterday was %B %d, %Y.")
        elif 'yesterday' in query:
            target_date = now - datetime.timedelta(days=1)
            response = target_date.strftime("Yesterday's date was %B %d, %Y.")
        elif 'date after tomorrow' in query:
            target_date = now + datetime.timedelta(days=2)
            response = target_date.strftime("The date for the day after tomorrow will be %B %d, %Y.")
        elif 'tomorrow' in query:
            target_date = now + datetime.timedelta(days=1)
            response = target_date.strftime("Tomorrow's date will be %B %d, %Y.")
        else:
            response = now.strftime("The date today is %B %d, %Y.")
        speak(response)
    
    
    # Day information
    elif 'day' in query and 'date' not in query:
        if 'day before yesterday' in query:
            target_day = now - datetime.timedelta(days=2)
            response = target_day.strftime("The day before yesterday was %A.")
        elif 'yesterday' in query:
            target_day = now - datetime.timedelta(days=1)
            response = target_day.strftime("Yesterday was %A.")
        elif 'day after tomorrow' in query:
            target_day = now + datetime.timedelta(days=2)
            response = target_day.strftime("The day after tomorrow will be %A.")
        elif 'tomorrow' in query:
            target_day = now + datetime.timedelta(days=1)
            response = target_day.strftime("Tomorrow will be %A.")
        else:
            response = now.strftime("Today is %A.")
        speak(response)
    
    # Open websites
    elif 'open youtube' in query:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    
    elif 'open google' in query:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    
    # Play music
    elif 'play music' in query:
        music_dir = "c:/Users/Prakamya Singh/OneDrive/Desktop/MP/Songs"
        try:
           songs = os.listdir(music_dir)
           if songs:
            # Optionally, shuffle the songs if desired
               random.shuffle(songs)
            # Path to Windows Media Player (update if needed)
               wmplayer_path = r"C:\Program Files\Windows Media Player\wmplayer.exe"
               for song in songs:
                   full_path = os.path.join(music_dir, song)
                   speak(f"Now playing {song}")
                # Launch Windows Media Player to play the song and wait until it finishes:
                   subprocess.call([wmplayer_path, "/play", "/close", full_path])
           else:
               speak("No music files found")
        except Exception as e:
            speak("Music directory not found")

    
    # Open applications
    elif 'open notepad' in query:
        speak("Opening Notepad")
        os.system("notepad")
    
    # Exit command (using voice or key press)
    elif 'exit' in query or 'goodbye' in query or keyboard.is_pressed("q"):  # Press 'q' to exit program
        speak("Goodbye! Have a nice day.")
        exit_program = True
    
    # Default response
    else:
        speak("Let me think...")
        deepseek_response = deepseek_chat(query)
        speak(deepseek_response)

    
    return True


# Main function with key detection for skipping and exiting
def main():
    global exit_program
    
    wish_user()
    
    while not exit_program:
        query = listen()
        
        if query != "None":
            process_command(query)

    
if __name__ == "__main__":
    main()
