import os
import sys
import webbrowser
import threading
import eel
from backend.auth import recoganize
from backend.feature import *
from backend.command import *
from backend.config import ENABLE_FACE_AUTH

def start():
    eel.init("frontend") 
    
    # Play assistant sound at start
    play_assistant_sound()
    
    # Start the hotword listener loop in a background thread
    print("Initializing Hotword Detector Thread...")
    threading.Thread(target=hotword, daemon=True).start()
    
    @eel.expose
    def init():
        eel.hideLoader()
        
        # Check if Face Authentication is enabled
        if not ENABLE_FACE_AUTH:
            speak("Welcome to Your Assistant, Sir.")
            eel.hideStart()
            play_assistant_sound()
            return
            
        # Check if trainer.yml exists. If not, trigger Setup Wizard
        trainer_path = os.path.join("backend", "auth", "trainer", "trainer.yml")
        if not os.path.exists(trainer_path):
            speak("Welcome to Jarvis. I see that your security credentials are not registered. Let us begin face enrollment, Sir.")
            eel.showSetupWizard()()
        else:
            speak("Welcome to Jarvis. Ready for Face Authentication.")
            flag = recoganize.AuthenticateFace()
            if flag == 1:
                speak("Face recognized successfully.")
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                speak("Welcome to Your Assistant, Sir.")
                eel.hideStart()
                play_assistant_sound()
            else:
                speak("Face not recognized, Sir.")
                eel.showAuthRetry()()
                
    # Open UI in default web browser
    webbrowser.open("http://127.0.0.1:8000/index.html")
    
    eel.start("index.html", mode=None, host="localhost", block=True)
