import re
import sys
import time
import subprocess
import speech_recognition as sr
import eel

from backend.config import TTS_VOICE, TTS_RATE


def speak(text):
    """Speak text using high-quality macOS 'say' command (Evan voice) or pyttsx3 fallback."""
    text = str(text).strip()
    if not text:
        return

    # Update UI with the response text
    try:
        eel.DisplayMessage(text)
        eel.receiverText(text)
    except Exception:
        pass

    if sys.platform == "darwin":
        # Use macOS native 'say' for crisp, Alexa-quality TTS
        try:
            subprocess.run(
                ["say", "-v", TTS_VOICE, "-r", str(TTS_RATE), text],
                check=True, timeout=60
            )
        except FileNotFoundError:
            # Fallback if 'say' is somehow missing
            _pyttsx3_speak(text)
        except subprocess.TimeoutExpired:
            print("TTS timed out.")
        except Exception as e:
            print(f"TTS error: {e}")
            _pyttsx3_speak(text)
    else:
        _pyttsx3_speak(text)


def _pyttsx3_speak(text):
    """Fallback TTS using pyttsx3 for non-macOS platforms."""
    try:
        import pyttsx3
        if sys.platform == "win32":
            engine = pyttsx3.init('sapi5')
        else:
            engine = pyttsx3.init()

        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        elif len(voices) > 0:
            engine.setProperty('voice', voices[0].id)

        engine.setProperty('rate', TTS_RATE)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except ImportError:
        print(f"TTS fallback failed: pyttsx3 is not installed. Please print: {text}")
    except Exception as e:
        print(f"pyttsx3 fallback error: {e}")


def takecommand():
    """Listen for voice input and return recognized text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        try:
            eel.DisplayMessage("I'm listening...")
        except Exception:
            pass
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None

    try:
        print("Recognizing...")
        try:
            eel.DisplayMessage("Recognizing...")
        except Exception:
            pass
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        try:
            eel.DisplayMessage(query)
        except Exception:
            pass
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()


@eel.expose
def takeAllCommands(message=None):
    """Main command router — dispatches voice/text input to the appropriate handler."""
    if message is None:
        query = takecommand()
        if not query:
            try:
                eel.ShowHood()
            except Exception:
                pass
            return
        print(query)
        try:
            eel.senderText(query)
        except Exception:
            pass
    else:
        query = str(message).lower().strip()
        print(f"Message received: {query}")
        try:
            eel.senderText(query)
        except Exception:
            pass

    try:
        if query:
            _dispatch_command(query)
        else:
            speak("No command was given.")
    except Exception as e:
        print(f"An error occurred: {e}")
        speak("Sorry, something went wrong.")

    try:
        eel.ShowHood()
    except Exception:
        pass


def _dispatch_command(query):
    """Route query to the correct feature handler."""
    # --- Time & Date ---
    if "what time" in query or "what's the time" in query or "current time" in query:
        from backend.feature import tellTime
        tellTime()

    elif "what date" in query or "what's the date" in query or "today's date" in query:
        from backend.feature import tellDate
        tellDate()

    # --- Weather ---
    elif "weather" in query:
        from backend.feature import getWeather
        getWeather(query)

    # --- Jokes ---
    elif "joke" in query or "make me laugh" in query:
        from backend.feature import tellJoke
        tellJoke()

    # --- Timer ---
    elif "set a timer" in query or "timer for" in query or "set timer" in query:
        from backend.feature import setTimer
        setTimer(query)

    # --- Wikipedia ---
    elif "who is" in query or "what is" in query or "tell me about" in query or "wikipedia" in query:
        from backend.feature import wikiSearch
        wikiSearch(query)

    # --- Math ---
    elif "calculate" in query or "what is" in query and any(op in query for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
        from backend.feature import calculate
        calculate(query)

    # --- System Sleep / Lock ---
    elif "go to sleep" in query or "lock screen" in query or "lock the screen" in query:
        from backend.feature import systemSleep
        systemSleep()

    # --- Volume control ---
    elif "set volume to" in query or "volume to" in query:
        from backend.feature import setVolume
        match = re.search(r'\d+', query)
        if match:
            setVolume(int(match.group()))
        else:
            speak("Please specify a percentage, Sir.")
    elif "mute" in query:
        from backend.feature import setVolume
        setVolume(0)
    elif "unmute" in query:
        from backend.feature import setVolume
        setVolume(50)

    # --- Brightness control ---
    elif "brightness up" in query or "increase brightness" in query:
        from backend.feature import brightnessUp
        brightnessUp()
    elif "brightness down" in query or "decrease brightness" in query:
        from backend.feature import brightnessDown
        brightnessDown()

    # --- System status ---
    elif "system stats" in query or "system status" in query or "battery" in query:
        from backend.feature import getSystemStats
        getSystemStats()

    # --- Media control ---
    elif "pause" in query and ("music" in query or "song" in query):
        from backend.feature import mediaControl
        mediaControl("pause")
    elif ("play" in query or "resume" in query) and ("music" in query or "song" in query):
        from backend.feature import mediaControl
        mediaControl("play")
    elif "next" in query and ("track" in query or "song" in query):
        from backend.feature import mediaControl
        mediaControl("next")
    elif "previous" in query and ("track" in query or "song" in query):
        from backend.feature import mediaControl
        mediaControl("previous")

    # --- Screenshot ---
    elif "screenshot" in query or "capture screen" in query:
        from backend.feature import takeScreenshot
        takeScreenshot()

    # --- Vision ---
    elif "what do you see" in query or "look at this" in query or "analyze camera" in query:
        from backend.feature import jarvisVision
        jarvisVision()

    # --- Open app/website ---
    elif "open" in query:
        from backend.feature import openCommand
        openCommand(query)

    # --- WhatsApp ---
    elif "send message" in query or "video call" in query or ("call" in query and "whatsapp" in query):
        from backend.feature import findContact, whatsApp
        Phone, name = findContact(query)
        if Phone != 0:
            flag = ""
            if "send message" in query:
                flag = 'message'
                speak("What message to send?")
                query = takecommand()
            elif "video call" in query:
                flag = 'video call'
            else:
                flag = 'call'
            whatsApp(Phone, query, flag, name)

    # --- YouTube ---
    elif "on youtube" in query:
        from backend.feature import PlayYoutube
        PlayYoutube(query)

    # --- News ---
    elif "news" in query or "headlines" in query:
        from backend.feature import getNews
        getNews()

    # --- Fallback to AI chatbot ---
    else:
        from backend.feature import chatBot
        chatBot(query)