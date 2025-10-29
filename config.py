import os

# Bot Token - Get from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Download directory
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')

# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
