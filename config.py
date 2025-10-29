import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
