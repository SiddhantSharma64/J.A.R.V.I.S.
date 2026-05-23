"""
J.A.R.V.I.S. Database Initialization
Creates and seeds SQLite tables for system commands, web commands, and contacts.
Run this file directly to reset and seed the database: python -m backend.db
"""

import os
import sys
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jarvis.db")


def get_connection():
    """Return a SQLite connection to the Jarvis database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
    return conn


def initialize_database():
    """Create all required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sys_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE,
            path VARCHAR(1000)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE,
            url VARCHAR(1000)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200),
            Phone VARCHAR(255),
            email VARCHAR(255) DEFAULT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            remind_at TIMESTAMP,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print("Database tables initialized.")


def seed_macos_apps():
    """Seed common macOS application paths."""
    conn = get_connection()
    cursor = conn.cursor()

    # macOS system apps
    mac_apps = [
        ("safari", "/Applications/Safari.app"),
        ("finder", "/System/Library/CoreServices/Finder.app"),
        ("terminal", "/Applications/Utilities/Terminal.app"),
        ("calculator", "/Applications/Calculator.app"),
        ("notes", "/Applications/Notes.app"),
        ("calendar", "/Applications/Calendar.app"),
        ("photos", "/Applications/Photos.app"),
        ("music", "/Applications/Music.app"),
        ("maps", "/Applications/Maps.app"),
        ("facetime", "/Applications/FaceTime.app"),
        ("messages", "/Applications/Messages.app"),
        ("mail", "/Applications/Mail.app"),
        ("preview", "/Applications/Preview.app"),
        ("app store", "/Applications/App Store.app"),
        ("system preferences", "/Applications/System Preferences.app"),
        ("system settings", "/Applications/System Settings.app"),
        ("activity monitor", "/Applications/Utilities/Activity Monitor.app"),
        ("text edit", "/Applications/TextEdit.app"),
        ("xcode", "/Applications/Xcode.app"),
        ("visual studio code", "/Applications/Visual Studio Code.app"),
        ("vs code", "/Applications/Visual Studio Code.app"),
        ("spotify", "/Applications/Spotify.app"),
        ("discord", "/Applications/Discord.app"),
        ("slack", "/Applications/Slack.app"),
        ("chrome", "/Applications/Google Chrome.app"),
        ("google chrome", "/Applications/Google Chrome.app"),
        ("firefox", "/Applications/Firefox.app"),
        ("whatsapp", "/Applications/WhatsApp.app"),
        ("telegram", "/Applications/Telegram.app"),
        ("notion", "/Applications/Notion.app"),
    ]

    for name, path in mac_apps:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO sys_command (name, path) VALUES (?, ?)",
                (name, path)
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print(f"Seeded {len(mac_apps)} macOS app entries.")


def seed_web_commands():
    """Seed common web commands."""
    conn = get_connection()
    cursor = conn.cursor()

    web_commands = [
        ("google", "https://www.google.com"),
        ("youtube", "https://www.youtube.com"),
        ("gmail", "https://mail.google.com"),
        ("github", "https://github.com"),
        ("stackoverflow", "https://stackoverflow.com"),
        ("stack overflow", "https://stackoverflow.com"),
        ("linkedin", "https://www.linkedin.com"),
        ("twitter", "https://twitter.com"),
        ("reddit", "https://www.reddit.com"),
        ("amazon", "https://www.amazon.com"),
        ("netflix", "https://www.netflix.com"),
        ("chatgpt", "https://chat.openai.com"),
        ("wikipedia", "https://www.wikipedia.org"),
        ("instagram", "https://www.instagram.com"),
        ("facebook", "https://www.facebook.com"),
        ("notion", "https://www.notion.so"),
    ]

    for name, url in web_commands:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO web_command (name, url) VALUES (?, ?)",
                (name, url)
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print(f"Seeded {len(web_commands)} web command entries.")


# Auto-initialize on import
initialize_database()


if __name__ == "__main__":
    print("Resetting and seeding J.A.R.V.I.S. database...")
    seed_macos_apps()
    seed_web_commands()
    print("Database setup complete!")