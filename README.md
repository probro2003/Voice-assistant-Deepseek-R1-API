# Voice-assistant-Deepseek-R1-API
🗣️ MANA: Your AI-Powered Desktop Voice Assistant
MANA (Multifunctional AI-based Natural Assistant) is a smart and interactive voice assistant built with Python for Windows desktop. It responds to your voice, controls your system, answers general questions using DeepSeek (via OpenRouter), and even lets you interrupt its speech — all through natural language and keyboard input.

✨ Features
🎙️ Speech Recognition
Understands voice commands using Google Speech Recognition API.

🔊 Text-to-Speech (TTS)
Speaks responses aloud using the offline pyttsx3 engine.

🧠 AI Chat Integration (NLP)
Uses DeepSeek's R1 model via OpenRouter API to answer general questions conversationally.

🖥️ System Control via Voice
Adjust volume, brightness, night light, and battery saver settings without lifting a finger.

🔍 Smart Google Search
Searches the web and opens the top result when asked.

🎵 Play Local Music
Accesses and plays songs from a specified folder on your PC.

📅 Time, Date, and Day Queries
Answers natural queries like "What's tomorrow's date?" or "What day was it yesterday?"

🧠 Interruptible Speaking
Press Spacebar anytime while MANA is speaking to stop the response midway and issue a new command.

🛡️ Secure API Key Management
Stores your OpenRouter API key in a .env file (not uploaded to GitHub).

🛠️ Technologies Used
speech_recognition — voice-to-text

pyttsx3 — offline text-to-speech

keyboard — interrupt control

threading — parallel keyboard listening

openai (OpenRouter) — chat-based AI via DeepSeek model

dotenv — environment variable loader for secure keys

screen_brightness_control, pycaw, subprocess, webbrowser, etc.

⚙️ Setup Instructions
Install requirements:

bash
Copy code
pip install -r requirements.txt
Create a .env file in the project folder:

ini
Copy code
OPENROUTER_API_KEY=your_actual_api_key_here
Ensure these folders exist (or change the path in the code):

swift
Copy code
c:/Users/Prakamya Singh/OneDrive/Desktop/MP/Songs
Run the assistant:

bash
Copy code
python voiceassistant.py
🧪 Example Voice Commands
"Increase volume"

"Decrease brightness"

"Play music"

"Search Python history"

"What's the date after tomorrow?"

"What is the capital of Japan?"

"Open YouTube"

"Goodbye" (to exit)

🛑 Security Tip
Your .env file should be excluded from GitHub. Make sure .gitignore contains:

bash
Copy code
.env
__pycache__/
*.pyc
✅ Future Ideas (if you want to expand)
Add task scheduling (like reminders)

Integrate local NLP for offline fallback

Add GUI for manual override

Allow multi-turn conversations (context memory)
