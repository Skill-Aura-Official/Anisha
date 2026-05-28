import json
import os
from config import OWNER_ID

DB_FILE = "db.json"

def load_db():
    default_structure = {
        "cofounders": [],
        "managers": [],
        "gbanned": [],
        "served_chats": [],
        "served_users": []
    }
    if not os.path.exists(DB_FILE):
        return default_structure
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all keys exist
            for key, default_val in default_structure.items():
                if key not in data:
                    data[key] = default_val
            return data
    except:
        return default_structure

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving database: {e}")

def get_served_chats():
    return load_db().get("served_chats", [])

def add_served_chat(chat_id: int):
    db = load_db()
    if "served_chats" not in db:
        db["served_chats"] = []
    if chat_id not in db["served_chats"]:
        db["served_chats"].append(chat_id)
        save_db(db)

def remove_served_chat(chat_id: int):
    db = load_db()
    if "served_chats" in db and chat_id in db["served_chats"]:
        db["served_chats"].remove(chat_id)
        save_db(db)

def get_served_users():
    return load_db().get("served_users", [])

def add_served_user(user_id: int):
    db = load_db()
    if "served_users" not in db:
        db["served_users"] = []
    if user_id not in db["served_users"]:
        db["served_users"].append(user_id)
        save_db(db)

def add_cofounder_db(user_id: int):
    db = load_db()
    if user_id not in db["cofounders"]:
        db["cofounders"].append(user_id)
        save_db(db)

def remove_cofounder_db(user_id: int):
    db = load_db()
    if user_id in db["cofounders"]:
        db["cofounders"].remove(user_id)
        save_db(db)

def add_manager_db(user_id: int):
    db = load_db()
    if user_id not in db["managers"]:
        db["managers"].append(user_id)
        save_db(db)

def remove_manager_db(user_id: int):
    db = load_db()
    if user_id in db["managers"]:
        db["managers"].remove(user_id)
        save_db(db)

def add_gbanned_db(user_id: int):
    db = load_db()
    if user_id not in db["gbanned"]:
        db["gbanned"].append(user_id)
        save_db(db)

def remove_gbanned_db(user_id: int):
    db = load_db()
    if user_id in db["gbanned"]:
        db["gbanned"].remove(user_id)
        save_db(db)
