import os
from PyQt5.QtWidgets import QFileDialog
from constants import DEFAULT_DOWNLOAD_PATH

def get_download_directory(parent):
    download_dir = QFileDialog.getExistingDirectory(
        parent, 
        "Select Download Directory", 
        os.path.expanduser(DEFAULT_DOWNLOAD_PATH)
    )
    return download_dir if download_dir else os.path.expanduser(DEFAULT_DOWNLOAD_PATH)

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB"

def validate_youtube_url(url):
    # Simple validation - could be enhanced
    return "youtube.com/" in url or "youtu.be/" in url

def get_safe_filename(title):
    # Remove invalid characters from filename
    invalid_chars = '<>:"/\\|?*'
    filename = ''.join(c for c in title if c not in invalid_chars)
    # Truncate if too long
    if len(filename) > 100:
        filename = filename[:97] + "..."
    return filename