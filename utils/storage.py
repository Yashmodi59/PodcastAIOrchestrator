import os
import json
import time
from datetime import datetime

def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("data/podcasts", exist_ok=True)
    os.makedirs("audio", exist_ok=True)

def save_user_preferences(user_id, preferences):
    """
    Save user preferences to a JSON file.
    
    Args:
        user_id (str): Unique identifier for the user.
        preferences (dict): User preferences to save.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    ensure_directories()
    
    try:
        user_dir = f"data/users/{user_id}"
        os.makedirs(user_dir, exist_ok=True)
        
        with open(f"{user_dir}/preferences.json", "w") as f:
            json.dump(preferences, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving user preferences: {e}")
        return False

def load_user_preferences(user_id):
    """
    Load user preferences from a JSON file.
    
    Args:
        user_id (str): Unique identifier for the user.
        
    Returns:
        dict: User preferences or an empty dict if not found.
    """
    ensure_directories()
    
    try:
        user_dir = f"data/users/{user_id}"
        pref_path = f"{user_dir}/preferences.json"
        
        if os.path.exists(pref_path):
            with open(pref_path, "r") as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"Error loading user preferences: {e}")
        return {}

def save_podcast(user_id, podcast_data):
    """
    Save podcast data to a JSON file.
    
    Args:
        user_id (str): Unique identifier for the user.
        podcast_data (dict): Podcast data to save.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    ensure_directories()
    
    try:
        podcast_id = podcast_data.get("id")
        if not podcast_id:
            podcast_id = f"{int(time.time())}"
            podcast_data["id"] = podcast_id
        
        # Ensure the podcast has a creation date
        if "date_created" not in podcast_data:
            podcast_data["date_created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to user's podcast list
        user_podcasts_dir = f"data/users/{user_id}/podcasts"
        os.makedirs(user_podcasts_dir, exist_ok=True)
        
        with open(f"{user_podcasts_dir}/{podcast_id}.json", "w") as f:
            json.dump(podcast_data, f, indent=2)
        
        # Also save to global podcast directory
        with open(f"data/podcasts/{podcast_id}.json", "w") as f:
            json.dump(podcast_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving podcast: {e}")
        return False

def load_podcasts(user_id):
    """
    Load all podcasts for a user.
    
    Args:
        user_id (str): Unique identifier for the user.
        
    Returns:
        list: List of podcast data dictionaries.
    """
    ensure_directories()
    
    try:
        user_podcasts_dir = f"data/users/{user_id}/podcasts"
        
        if not os.path.exists(user_podcasts_dir):
            return []
        
        podcasts = []
        
        for filename in os.listdir(user_podcasts_dir):
            if filename.endswith(".json"):
                try:
                    with open(f"{user_podcasts_dir}/{filename}", "r") as f:
                        podcast_data = json.load(f)
                        podcasts.append(podcast_data)
                except Exception as e:
                    print(f"Error loading podcast file {filename}: {e}")
        
        # Sort by date created (newest first)
        podcasts.sort(key=lambda x: x.get("date_created", ""), reverse=True)
        
        return podcasts
    except Exception as e:
        print(f"Error loading podcasts: {e}")
        return []

def load_podcast(podcast_id):
    """
    Load a specific podcast by ID.
    
    Args:
        podcast_id (str): Unique identifier for the podcast.
        
    Returns:
        dict: Podcast data or None if not found.
    """
    ensure_directories()
    
    try:
        podcast_path = f"data/podcasts/{podcast_id}.json"
        
        if os.path.exists(podcast_path):
            with open(podcast_path, "r") as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        print(f"Error loading podcast: {e}")
        return None

def save_subscriber(email):
    """
    Save a subscriber email to the subscribers list.
    
    Args:
        email (str): Subscriber email address.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        # Load existing subscribers
        subscribers = load_subscribers()
        
        # Add new subscriber if not already in the list
        if email not in subscribers:
            subscribers.append(email)
            
            # Save updated list
            with open("data/subscribers.json", "w") as f:
                json.dump({"subscribers": subscribers}, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving subscriber: {e}")
        return False

def load_subscribers():
    """
    Load the list of subscriber emails.
    
    Returns:
        list: List of subscriber email addresses.
    """
    ensure_directories()
    
    try:
        subscribers_path = "data/subscribers.json"
        
        if os.path.exists(subscribers_path):
            with open(subscribers_path, "r") as f:
                data = json.load(f)
                return data.get("subscribers", [])
        else:
            return []
    except Exception as e:
        print(f"Error loading subscribers: {e}")
        return []
