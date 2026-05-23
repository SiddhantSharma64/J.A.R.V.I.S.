import os
import re
import sys
import json
import time
import struct
import subprocess
import webbrowser
import base64
import sqlite3
import datetime
import threading
import urllib.request
import urllib.parse
from shlex import quote

import eel
import pygame
import pywhatkit as kit
import numpy as np

from backend.command import speak
from backend.config import ASSISTANT_NAME, NVIDIA_API_KEY, COUNTRY_CODE
from backend.helper import extract_yt_term, remove_words

# Initialize pygame mixer for sound effects
pygame.mixer.init()

# Global chat memory for Kimi chatbot
chat_memory = []

def get_db_connection():
    conn = sqlite3.connect("jarvis.db", check_same_thread=False)
    return conn

@eel.expose
def play_assistant_sound():
    sound_file = os.path.join("frontend", "assets", "audio", "start_sound.mp3")
    if os.path.exists(sound_file):
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower()
    app_name = query.strip()

    if app_name != "":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening " + app_name)
                if sys.platform == "darwin":
                    subprocess.call(["open", results[0][0]])
                elif sys.platform == "win32":
                    os.startfile(results[0][0])
                else:
                    subprocess.call(["xdg-open", results[0][0]])
            else: 
                cursor.execute('SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                if len(results) != 0:
                    speak("Opening " + app_name)
                    webbrowser.open(results[0][0])
                else:
                    speak("Opening " + app_name)
                    try:
                        if sys.platform == "darwin":
                            subprocess.call(["open", "-a", app_name])
                        elif sys.platform == "win32":
                            os.system('start ' + app_name)
                        else:
                            os.system('xdg-open ' + app_name)
                    except:
                        speak("not found")
            conn.close()
        except Exception as e:
            print(f"Error in openCommand: {e}")
            speak("something went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:
        speak("Playing " + search_term + " on YouTube")
        kit.playonyt(search_term)
    else:
        speak("I couldn't extract the search term, Sir.")

def hotword():
    import speech_recognition as sr
    r = sr.Recognizer()
    m = sr.Microphone()
    print("Calibrating wake word microphone feed...")
    try:
        with m as source:
            r.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        print(f"Microphone calibration error: {e}")
        return

    # Debounce variable to prevent rapid re-triggering
    last_trigger = 0

    def callback(recognizer, audio):
        nonlocal last_trigger
        try:
            query = recognizer.recognize_google(audio, language='en-US').lower()
            print(f"[Wake Loop] Heard: '{query}'")
            if ("jarvis" in query or "alexa" in query) and (time.time() - last_trigger > 4):
                print("Wake word detected!")
                last_trigger = time.time()
                try:
                    eel.triggerListen()()
                except Exception as ex:
                    print(f"Eel callback error: {ex}")
        except sr.UnknownValueError:
            pass 
        except Exception as e:
            print(f"Background listener error: {e}")

    print("Wake word listener active. Say 'Jarvis' or 'Alexa' to activate.")
    stop_listening = r.listen_in_background(m, callback, phrase_time_limit=4)
    while True:
        time.sleep(1)

def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            speak("Contact not found, Sir.")
            return 0, 0
            
        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+'):
            mobile_number_str = COUNTRY_CODE + mobile_number_str

        return mobile_number_str, query
    except Exception as e:
        print(f"Error finding contact: {e}")
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(Phone, message, flag, name):
    import pyautogui
    if flag == 'message':
        target_tab = 12
        jarvis_message = "message sent successfully to " + name
    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to " + name
    else:
        target_tab = 6
        message = ''
        jarvis_message = "starting video call with " + name

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    if sys.platform == "darwin":
        subprocess.run(["open", whatsapp_url])
        time.sleep(5)
        pyautogui.hotkey('command', 'f')
    else:
        full_command = f'start "" "{whatsapp_url}"'
        subprocess.run(full_command, shell=True)
        time.sleep(5)
        pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# ==================== NEW FEATURES ====================

def tellTime():
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"Sir, the time is {time_str}")

def tellDate():
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today is {date_str}, Sir.")

def getWeather(query):
    speak("Checking the weather, Sir.")
    try:
        req = urllib.request.Request("https://wttr.in/?format=3", headers={'User-Agent': 'curl/7.64.1'})
        with urllib.request.urlopen(req, timeout=5) as response:
            weather = response.read().decode('utf-8').strip()
            speak(f"The current weather is: {weather}")
    except Exception as e:
        speak("I am unable to retrieve weather data at the moment, Sir.")

def tellJoke():
    try:
        req = urllib.request.Request("https://v2.jokeapi.dev/joke/Any?type=single", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            joke = data.get("joke", "I can't think of a joke right now, Sir.")
            speak(joke)
    except Exception as e:
        speak("My humor subroutines are currently offline, Sir.")

def setTimer(query):
    match = re.search(r'(\d+)\s*(minute|minutes|second|seconds|hour|hours)', query)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        total_seconds = amount
        if 'minute' in unit:
            total_seconds *= 60
        elif 'hour' in unit:
            total_seconds *= 3600
        
        speak(f"Setting a timer for {amount} {unit}, Sir.")
        def timer_done():
            speak("Sir, your timer has finished.")
            play_assistant_sound()
        
        t = threading.Timer(total_seconds, timer_done)
        t.start()
    else:
        speak("I didn't catch the duration for the timer, Sir. Please specify minutes or seconds.")

def wikiSearch(query):
    query = query.replace("wikipedia", "").replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
    if not query:
        speak("What should I search on Wikipedia, Sir?")
        return
    speak(f"Searching Wikipedia for {query}...")
    try:
        url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro&explaintext&titles=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data['query']['pages']
            page = list(pages.values())[0]
            if 'extract' in page:
                summary = page['extract'][:500]
                speak(f"According to Wikipedia: {summary.split('.')[0]}.")
            else:
                speak("I couldn't find anything on Wikipedia for that, Sir.")
    except Exception as e:
        speak("I encountered an error accessing Wikipedia, Sir.")

def calculate(query):
    speak("Calculating, Sir...")
    try:
        query = query.replace("calculate", "").replace("what is", "").strip()
        query = query.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/").replace("x", "*")
        query = re.sub(r'[^0-9\+\-\*\/\(\)\.]', '', query)
        if not query:
            speak("Invalid mathematical expression, Sir.")
            return
        result = eval(query, {"__builtins__": None}, {})
        speak(f"The answer is {result}, Sir.")
    except Exception as e:
        speak("I could not perform that calculation, Sir.")

def systemSleep():
    speak("Putting the system to sleep. Goodnight, Sir.")
    if sys.platform == "darwin":
        subprocess.run(["pmset", "sleepnow"])
    else:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def getNews():
    speak("Fetching the latest headlines, Sir.")
    try:
        url = "https://news.google.com/rss"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read().decode('utf-8')
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            if items:
                speak("Here are the top 3 headlines.")
                for i in range(min(3, len(items))):
                    title = items[i].find('title').text
                    speak(f"Headline {i+1}: {title}")
            else:
                speak("I couldn't find any news items, Sir.")
    except Exception as e:
        speak("I'm unable to fetch the news right now, Sir.")


# ==================== NVIDIA KIMI K2.6 CHATBOT INTEGRATION ====================

def chatBot(query):
    import requests
    global chat_memory
    user_input = query.lower()
    
    if not NVIDIA_API_KEY:
        speak("NVIDIA API key is not configured, Sir.")
        return "NVIDIA API key not set."

    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are J.A.R.V.I.S., a highly advanced, polite, and intelligent AI assistant "
        "created by Tony Stark. Respond in a sophisticated, concise, and helpful manner "
        "suitable for a voice assistant. Address the user as 'Sir'."
    )

    if not chat_memory:
        chat_memory.append({"role": "system", "content": system_prompt})
        
    chat_memory.append({"role": "user", "content": user_input})
    
    # Prune memory to prevent context explosion
    if len(chat_memory) > 11:
        chat_memory = [chat_memory[0]] + chat_memory[-10:]

    payload = {
        "model": "moonshotai/kimi-k2.6",
        "messages": chat_memory,
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 1.0,
        "stream": True,
        "chat_template_kwargs": {"thinking": True},
    }

    try:
        response = requests.post(invoke_url, headers=headers, json=payload, stream=True, timeout=30)
        eel.startChatbotStream()()
        
        reasoning_text = ""
        content_text = ""
        in_think_tag = False

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0]["delta"]
                        
                        if "reasoning_content" in delta and delta["reasoning_content"]:
                            r_chunk = delta["reasoning_content"]
                            reasoning_text += r_chunk
                            try: eel.streamThinking(r_chunk)()
                            except: pass
                            
                        if "content" in delta and delta["content"]:
                            c_chunk = delta["content"]
                            if "<think>" in c_chunk:
                                in_think_tag = True
                                parts = c_chunk.split("<think>")
                                if parts[0]:
                                    content_text += parts[0]
                                    try: eel.streamContent(parts[0])()
                                    except: pass
                                if len(parts) > 1 and parts[1]:
                                    reasoning_text += parts[1]
                                    try: eel.streamThinking(parts[1])()
                                    except: pass
                            elif "</think>" in c_chunk:
                                in_think_tag = False
                                parts = c_chunk.split("</think>")
                                if parts[0]:
                                    reasoning_text += parts[0]
                                    try: eel.streamThinking(parts[0])()
                                    except: pass
                                if len(parts) > 1 and parts[1]:
                                    content_text += parts[1]
                                    try: eel.streamContent(parts[1])()
                                    except: pass
                            else:
                                if in_think_tag:
                                    reasoning_text += c_chunk
                                    try: eel.streamThinking(c_chunk)()
                                    except: pass
                                else:
                                    content_text += c_chunk
                                    try: eel.streamContent(c_chunk)()
                                    except: pass
                    except:
                        pass
        
        content_text = content_text.replace("<think>", "").replace("</think>", "").strip()
        try: eel.endChatbotStream()()
        except: pass

        if content_text:
            chat_memory.append({"role": "assistant", "content": content_text})
            
            # If the response is very long, summarize it for TTS
            if len(content_text.split()) > 40:
                summary = content_text.split('.')[0] + "."
                speak(f"Sir, here is a detailed response on your screen. In summary: {summary}")
            else:
                speak(content_text)
        else:
            speak("I could not formulate a response, Sir.")
            
        return content_text
    except Exception as e:
        print(f"Error in chatBot Kimi API: {e}")
        speak("I encountered an issue connecting to my mainframe servers, Sir.")
        try: eel.endChatbotStream()()
        except: pass
        return "Error in chatbot."

# ==================== macOS SYSTEM CONTROLS ====================

def setVolume(percent):
    try:
        percent = int(percent)
        percent = max(0, min(100, percent))
        subprocess.run(["osascript", "-e", f"set volume output volume {percent}"])
        speak(f"Volume set to {percent} percent, Sir.")
    except Exception as e:
        speak("Could not adjust volume, Sir.")

def brightnessUp():
    try:
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 144'])
        speak("Brightness increased, Sir.")
    except:
        speak("Could not adjust brightness, Sir.")

def brightnessDown():
    try:
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 145'])
        speak("Brightness decreased, Sir.")
    except:
        speak("Could not adjust brightness, Sir.")

def getSystemStats():
    try:
        battery_output = subprocess.check_output(["pmset", "-g", "batt"]).decode("utf-8")
        battery_pct = "Unknown"
        charging_status = "not charging"
        pct_match = re.search(r"(\d+)%", battery_output)
        if pct_match:
            battery_pct = pct_match.group(1)
        if "charging" in battery_output and "discharging" not in battery_output:
            charging_status = "charging"
            
        cpu_output = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode("utf-8").strip()
        ram_output = subprocess.check_output(["sysctl", "hw.memsize"]).decode("utf-8").strip()
        mem_bytes = int(ram_output.split(":")[1].strip())
        mem_gb = mem_bytes / (1024 ** 3)
        
        stats_msg = f"Sir, the battery is at {battery_pct} percent and is {charging_status}. The load averages are {cpu_output}, and you have {mem_gb:.0f} gigabytes of system memory installed."
        speak(stats_msg)
    except Exception as e:
        speak("I was unable to retrieve system diagnostics, Sir.")

def mediaControl(action):
    try:
        if action == "play" or action == "pause":
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to playpause'])
            speak("Toggled playback, Sir.")
        elif action == "next":
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to next track'])
            speak("Skipping track, Sir.")
        elif action == "previous":
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to previous track'])
            speak("Playing previous track, Sir.")
    except:
        speak("Could not execute media command, Sir.")

def takeScreenshot():
    try:
        screenshot_dir = os.path.expanduser("~/Desktop")
        filepath = os.path.join(screenshot_dir, f"Jarvis_Screenshot_{int(time.time())}.png")
        subprocess.run(["screencapture", filepath])
        speak(f"Screenshot saved to your Desktop, Sir.")
    except Exception as e:
        speak("Failed to capture screenshot, Sir.")

# ==================== MULTIMODAL OPTICS (VISION) ====================

def jarvisVision(prompt="Describe what you see in front of the camera, Sir."):
    import cv2
    import requests
    speak("Activating optics, Sir...")
    
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        speak("I cannot access the camera feed, Sir.")
        return
        
    ret, frame = cam.read()
    cam.release()
    
    if not ret:
        speak("Failed to capture image, Sir.")
        return
        
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    if not NVIDIA_API_KEY:
        speak("API key not configured, Sir.")
        return
        
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are J.A.R.V.I.S., a highly advanced AI. Analyze the provided webcam image "
        "and answer the user's prompt in a sophisticated, concise, and helpful voice. "
        "Address the user as 'Sir'."
    )

    payload = {
        "model": "moonshotai/kimi-k2.6",
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{jpg_as_text}"}}
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 1.0,
        "stream": True,
        "chat_template_kwargs": {"thinking": True},
    }

    try:
        response = requests.post(invoke_url, headers=headers, json=payload, stream=True, timeout=30)
        eel.startChatbotStream()()
        content_text = ""
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0]["delta"]
                        if "content" in delta and delta["content"]:
                            c_chunk = delta["content"]
                            content_text += c_chunk
                            try: eel.streamContent(c_chunk)()
                            except: pass
                    except:
                        pass
                        
        content_text = content_text.replace("<think>", "").replace("</think>", "").strip()
        try: eel.endChatbotStream()()
        except: pass
        
        if content_text:
            speak(content_text)
        else:
            speak("Optics analysis resulted in an empty response, Sir.")
    except Exception as e:
        print(f"Error in vision Kimi API: {e}")
        speak("Apologies Sir, I failed to complete the optical analysis.")
        try: eel.endChatbotStream()()
        except: pass

# ==================== FACE ENROLLMENT PROCESS (SETUP WIZARD) ====================

@eel.expose
def enroll_face_process(name):
    import cv2
    from PIL import Image
    users_file = os.path.join("backend", "auth", "users.json")
    samples_dir = os.path.join("backend", "auth", "samples")
    trainer_dir = os.path.join("backend", "auth", "trainer")
    
    os.makedirs(samples_dir, exist_ok=True)
    os.makedirs(trainer_dir, exist_ok=True)
    
    users = {}
    if os.path.exists(users_file):
        try:
            with open(users_file, "r") as f:
                users = json.load(f)
        except Exception as e:
            print(f"Error reading users file: {e}")
            
    user_ids = [int(k) for k in users.keys()]
    new_id = max(user_ids) + 1 if user_ids else 1
    
    detector_path = os.path.join("backend", "auth", "haarcascade_frontalface_default.xml")
    if not os.path.exists(detector_path):
        eel.updateSetupWizardStatus("Error: Haar cascade file missing.")()
        speak("Security configuration file is missing, Sir.")
        return False
        
    detector = cv2.CascadeClassifier(detector_path)
    cam = cv2.VideoCapture(0)
    
    if not cam.isOpened():
        try: eel.updateSetupWizardStatus("Error: Camera not found.")()
        except: pass
        speak("I cannot access the camera for scanning, Sir.")
        return False
        
    count = 0
    speak("Camera active. Please look directly at the lens. Scan commencing, Sir.")
    
    while True:
        ret, img = cam.read()
        if not ret:
            try: eel.updateSetupWizardStatus("Error: Camera failed.")()
            except: pass
            break
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            count += 1
            sample_path = os.path.join(samples_dir, f"face.{new_id}.{count}.jpg")
            cv2.imwrite(sample_path, gray[y:y+h, x:x+w])
            try: eel.updateSetupWizardStatus(f"Scanning: {count}%")()
            except: pass
            
        if count >= 100:
            break
            
        time.sleep(0.05) 
        
    cam.release()
    cv2.destroyAllWindows()
    
    try: eel.updateSetupWizardStatus("Compiling biometric templates...")()
    except: pass
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    imagePaths = [os.path.join(samples_dir, f) for f in os.listdir(samples_dir) if f.endswith(".jpg")]
    faceSamples = []
    ids = []
    
    for imagePath in imagePaths:
        try:
            parts = os.path.split(imagePath)[-1].split(".")
            if len(parts) >= 3:
                curr_id = int(parts[1])
                if curr_id == new_id:
                    gray_img = Image.open(imagePath).convert('L')
                    img_arr = np.array(gray_img, 'uint8')
                    faces = detector.detectMultiScale(img_arr)
                    for (x, y, w, h) in faces:
                        faceSamples.append(img_arr[y:y+h, x:x+w])
                        ids.append(curr_id)
        except Exception as e:
            print(f"Error reading sample {imagePath}: {e}")
            
    if len(faceSamples) > 0:
        recognizer.train(faceSamples, np.array(ids))
        recognizer.write(os.path.join(trainer_dir, "trainer.yml"))
        
        users[str(new_id)] = name
        with open(users_file, "w") as f:
            json.dump(users, f)
            
        speak("Biometric configuration complete, Sir. Security database updated.")
        try: eel.setupWizardComplete()()
        except: pass
        return True
    else:
        try: eel.updateSetupWizardStatus("Error: Scan failed. No faces detected.")()
        except: pass
        speak("Scan failed, Sir. No faces detected.")
        return False

@eel.expose
def get_hud_metrics():
    try:
        batt_output = subprocess.check_output(["pmset", "-g", "batt"]).decode("utf-8")
        batt_match = re.search(r"(\d+)%", batt_output)
        batt = batt_match.group(1) + "%" if batt_match else "99%"
        
        ram_output = subprocess.check_output(["sysctl", "hw.memsize"]).decode("utf-8").strip()
        mem_bytes = int(ram_output.split(":")[1].strip())
        total_gb = round(mem_bytes / (1024 ** 3))
        
        cpu_load = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode("utf-8").strip().split()
        cpu = cpu_load[0] if cpu_load else "ACTIVE"
        
        return {"cpu": cpu, "ram": f"{total_gb} GB", "batt": batt}
    except Exception as e:
        print(f"Error fetching HUD metrics: {e}")
        return {"cpu": "ACTIVE", "ram": "16 GB", "batt": "100%"}