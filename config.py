import os
import logging

def get_required_env_var(name, default=None):
    """
    Get required environment variable with optional default.
    Raises ValueError if variable is not set and no default provided.
    """
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is required but not set!")
    return value

def setup_directories():
    """Create necessary directories for the bot."""
    # Base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Download directory
    download_dir = os.getenv('DOWNLOAD_DIR', os.path.join(BASE_DIR, 'downloads'))
    os.makedirs(download_dir, exist_ok=True)
    
    # Logs directory
    log_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Temp directory (for temporary downloads)
    temp_dir = os.path.join(BASE_DIR, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    return BASE_DIR, download_dir, log_dir, temp_dir

# Setup directories
BASE_DIR, DOWNLOAD_DIR, LOG_DIR, TEMP_DIR = setup_directories()

# ===== BOT CONFIGURATION =====
# Bot Token - REQUIRED
BOT_TOKEN = get_required_env_var('BOT_TOKEN')

# Bot Username (will be fetched automatically, but can be set manually)
BOT_USERNAME = os.getenv('BOT_USERNAME', '')

# Admin User IDs (comma-separated list of Telegram user IDs who have admin access)
ADMIN_IDS = []
admin_ids_str = os.getenv('ADMIN_IDS', '')
if admin_ids_str:
    try:
        ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',')]
    except ValueError:
        logging.warning(f"Invalid ADMIN_IDS format: {admin_ids_str}")

# ===== DOWNLOAD CONFIGURATION =====
# Maximum file size for Telegram (50MB is Telegram's limit)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

# Download timeout in seconds
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', '300'))  # 5 minutes

# Simultaneous downloads per user
MAX_SIMULTANEOUS_DOWNLOADS = int(os.getenv('MAX_SIMULTANEOUS_DOWNLOADS', '1'))

# ===== VIDEO/AUDIO QUALITY SETTINGS =====
# Audio quality settings
AUDIO_QUALITY = os.getenv('AUDIO_QUALITY', '192')  # kbps
AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'mp3')

# Video quality settings
VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', '720')  # max height
VIDEO_FORMAT = os.getenv('VIDEO_FORMAT', 'mp4')

# ===== NETWORK CONFIGURATION =====
# Proxy settings (optional)
PROXY = os.getenv('PROXY', None)

# Request timeout
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

# Retry settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))

# ===== SECURITY CONFIGURATION =====
# Allowed domains (comma-separated)
ALLOWED_DOMAINS = [
    'youtube.com',
    'youtu.be',
    'www.youtube.com',
    'm.youtube.com',
    'music.youtube.com'
]

# Add custom allowed domains from environment
custom_domains = os.getenv('ALLOWED_DOMAINS', '')
if custom_domains:
    ALLOWED_DOMAINS.extend([domain.strip() for domain in custom_domains.split(',')])

# Blocked domains (comma-separated)
BLOCKED_DOMAINS = []
blocked_domains_str = os.getenv('BLOCKED_DOMAINS', '')
if blocked_domains_str:
    BLOCKED_DOMAINS = [domain.strip() for domain in blocked_domains_str.split(',')]

# Rate limiting (requests per minute per user)
RATE_LIMIT = int(os.getenv('RATE_LIMIT', '10'))

# ===== PERFORMANCE CONFIGURATION =====
# Thread pool size for downloads
THREAD_POOL_SIZE = int(os.getenv('THREAD_POOL_SIZE', '2'))

# Cache settings
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENABLE_FILE_LOGGING = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))

# ===== RENDER-SPECIFIC SETTINGS =====
# Webhook settings for production
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
RENDER_PORT = int(os.getenv('PORT', '10000'))

# ===== FEATURE FLAGS =====
# Enable/disable features
ENABLE_AUDIO_DOWNLOAD = os.getenv('ENABLE_AUDIO_DOWNLOAD', 'true').lower() == 'true'
ENABLE_VIDEO_DOWNLOAD = os.getenv('ENABLE_VIDEO_DOWNLOAD', 'true').lower() == 'true'
ENABLE_PLAYLIST_DOWNLOAD = os.getenv('ENABLE_PLAYLIST_DOWNLOAD', 'false').lower() == 'true'

# ===== MESSAGE CONFIGURATION =====
# Welcome message
WELCOME_MESSAGE = """
👋 Welcome to YouTube Downloader Bot!

With this bot, you can download:
🎧 Audio — /audio <YouTube URL>
🎥 Video — /video <YouTube URL>

Example:
/audio https://youtube.com/watch?v=abcd1234
/video https://youtube.com/watch?v=abcd1234

Supported formats:
- MP3 (audio)
- MP4 (video)

Just send me a YouTube link to get started!
"""

# Help message
HELP_MESSAGE = """
📖 **Available Commands:**

/start - Show welcome message
/audio <link> - Download audio from YouTube
/video <link> - Download video from YouTube  
/stop - Cancel current download
/help - Show this help message

💡 **Tips:**
- You can also just send a YouTube link directly!
- Maximum file size: 50MB
- Supported: YouTube videos and shorts
"""

# ===== VALIDATION =====
def validate_config():
    """Validate configuration and log warnings for issues."""
    # Validate BOT_TOKEN format (basic check)
    if BOT_TOKEN and ':' not in BOT_TOKEN:
        logging.warning("BOT_TOKEN format seems invalid. Should be in format: '123456789:ABCdefGHIjklMnOpQRsTuvwxyz'")
    
    # Validate quality settings
    try:
        audio_quality = int(AUDIO_QUALITY)
        if audio_quality < 64 or audio_quality > 320:
            logging.warning(f"AUDIO_QUALITY {audio_quality} is outside typical range (64-320)")
    except ValueError:
        logging.warning(f"Invalid AUDIO_QUALITY: {AUDIO_QUALITY}")
    
    try:
        video_quality = int(VIDEO_QUALITY)
        if video_quality not in [144, 240, 360, 480, 720, 1080]:
            logging.warning(f"VIDEO_QUALITY {video_quality} is non-standard")
    except ValueError:
        logging.warning(f"Invalid VIDEO_QUALITY: {VIDEO_QUALITY}")
    
    # Check directory permissions
    for directory in [DOWNLOAD_DIR, LOG_DIR, TEMP_DIR]:
        if not os.access(directory, os.W_OK):
            logging.warning(f"Directory not writable: {directory}")

# Run validation when module is imported
validate_config()

# ===== CONFIGURATION SUMMARY =====
def print_config_summary():
    """Print a summary of the configuration (safe version without sensitive data)."""
    summary = f"""
=== Bot Configuration Summary ===
Base Directory: {BASE_DIR}
Download Directory: {DOWNLOAD_DIR}
Log Directory: {LOG_DIR}
Temp Directory: {TEMP_DIR}

Bot Token: {'✓ Set' if BOT_TOKEN else '✗ Missing'}
Bot Username: {BOT_USERNAME or 'Not set'}

Audio Settings: {AUDIO_QUALITY}kbps {AUDIO_FORMAT}
Video Settings: {VIDEO_QUALITY}p {VIDEO_FORMAT}

Max File Size: {MAX_FILE_SIZE / (1024*1024):.0f}MB
Download Timeout: {DOWNLOAD_TIMEOUT}s
Rate Limit: {RATE_LIMIT} requests/min

Allowed Domains: {', '.join(ALLOWED_DOMAINS[:3])}{'...' if len(ALLOWED_DOMAINS) > 3 else ''}
Blocked Domains: {', '.join(BLOCKED_DOMAINS) if BLOCKED_DOMAINS else 'None'}

Log Level: {LOG_LEVEL}
File Logging: {'Enabled' if ENABLE_FILE_LOGGING else 'Disabled'}
================================
"""
    print(summary)

# Print summary when module is imported (for debugging)
if __name__ != '__main__':
    print_config_summary()

# Export all settings for easy access
__all__ = [
    'BOT_TOKEN',
    'BOT_USERNAME',
    'ADMIN_IDS',
    'DOWNLOAD_DIR',
    'LOG_DIR',
    'TEMP_DIR',
    'BASE_DIR',
    'MAX_FILE_SIZE',
    'DOWNLOAD_TIMEOUT',
    'MAX_SIMULTANEOUS_DOWNLOADS',
    'AUDIO_QUALITY',
    'AUDIO_FORMAT',
    'VIDEO_QUALITY',
    'VIDEO_FORMAT',
    'PROXY',
    'REQUEST_TIMEOUT',
    'MAX_RETRIES',
    'RETRY_DELAY',
    'ALLOWED_DOMAINS',
    'BLOCKED_DOMAINS',
    'RATE_LIMIT',
    'THREAD_POOL_SIZE',
    'ENABLE_CACHE',
    'CACHE_TTL',
    'LOG_LEVEL',
    'ENABLE_FILE_LOGGING',
    'LOG_MAX_SIZE',
    'LOG_BACKUP_COUNT',
    'WEBHOOK_URL',
    'RENDER_PORT',
    'ENABLE_AUDIO_DOWNLOAD',
    'ENABLE_VIDEO_DOWNLOAD',
    'ENABLE_PLAYLIST_DOWNLOAD',
    'WELCOME_MESSAGE',
    'HELP_MESSAGE'
]
