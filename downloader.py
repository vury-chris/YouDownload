import os
import threading
from PyQt5.QtCore import QObject, pyqtSignal
import yt_dlp

class Downloader(QObject):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._current_task = None
        
    def download(self, url, format_type, quality, output_dir):
        if self._running:
            self.status_signal.emit("A download is already in progress")
            return
            
        self._running = True
        self._current_task = threading.Thread(
            target=self._download_task,
            args=(url, format_type, quality, output_dir)
        )
        self._current_task.daemon = True
        self._current_task.start()
    
    def _download_task(self, url, format_type, quality, output_dir):
        try:
            from constants import SUPPORTED_AUDIO_FORMATS
            
            # Clean up any leftover temporary files
            for file in os.listdir(output_dir):
                if file.endswith('.part') or file.endswith('.ytdl'):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except:
                        pass
            
            # Setup the output template
            output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
            
            # Use a very simple approach similar to the working code you shared
            if format_type in SUPPORTED_AUDIO_FORMATS:
                # Audio download - simplified
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'progress_hooks': [self._progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_type,
                        'preferredquality': quality.replace('kbps', ''),
                    }],
                }
            else:
                # Video download - super simplified approach (no format selection)
                ydl_opts = {
                    'format': 'best',  # Just get the best format available
                    'outtmpl': output_template,
                    'progress_hooks': [self._progress_hook],
                }
            
            # Get video info first
            self.status_signal.emit("Extracting video information...")
            
            with yt_dlp.YoutubeDL({'quiet': True}) as info_ydl:
                try:
                    info = info_ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'video')
                    self.status_signal.emit(f"Processing: {video_title}")
                except Exception as e:
                    # If info extraction fails, just proceed with download
                    self.status_signal.emit(f"Processing video...")
            
            # Perform the download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find downloaded file - look for newest file
            latest_file = None
            latest_time = 0
            
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                file_time = os.path.getmtime(file_path)
                
                # Check if this is newer than our current latest file
                if file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_path
            
            if not latest_file:
                raise Exception("Could not locate the downloaded file")
                
            self.status_signal.emit(f"Download complete: {os.path.basename(latest_file)}")
            self.progress_signal.emit(100)
            self.finished_signal.emit(True, latest_file)
                
        except Exception as e:
            self.status_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, "")
            
            # Try to clean up partial downloads
            try:
                for file in os.listdir(output_dir):
                    if file.endswith('.part') or file.endswith('.ytdl'):
                        os.remove(os.path.join(output_dir, file))
            except:
                pass
                
        finally:
            self._running = False
    
    def _progress_hook(self, d):
        if not self._running:
            raise Exception("Download cancelled")
            
        if d['status'] == 'downloading':
            # Safer progress calculation that handles None values
            percent = 0
            
            try:
                if 'total_bytes' in d and d['total_bytes']:
                    if 'downloaded_bytes' in d and d['downloaded_bytes']:
                        percent = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
                elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                    if 'downloaded_bytes' in d and d['downloaded_bytes']:
                        percent = int(d['downloaded_bytes'] / d['total_bytes_estimate'] * 100)
            except (TypeError, ZeroDivisionError):
                # If there's any error in calculation, use incremental progress
                # to show activity without exact percentage
                if hasattr(self, '_last_percent'):
                    self._last_percent = min(95, self._last_percent + 1)
                else:
                    self._last_percent = 10
                percent = self._last_percent
                
            # Ensure percent is within range
            percent = max(0, min(99, percent))
            self.progress_signal.emit(percent)
            
            # Add more detailed status information
            status_text = "Downloading..."
            
            # Only add detailed info if speed is available and valid
            try:
                if 'speed' in d and d['speed'] is not None:
                    speed = d['speed'] / 1024  # Convert to KB/s
                    if speed > 1024:
                        speed_str = f"{speed/1024:.1f} MB/s"
                    else:
                        speed_str = f"{speed:.1f} KB/s"
                        
                    status_text = f"Downloading: {percent}% ({speed_str})"
                    
                    # Add ETA if available
                    if 'eta' in d and d['eta'] is not None:
                        eta = d['eta']
                        if eta > 60:
                            eta_str = f"{eta//60}m {eta%60}s"
                        else:
                            eta_str = f"{eta}s"
                        status_text += f", ETA: {eta_str}"
            except:
                # If any calculation fails, use simple status text
                pass
                
            self.status_signal.emit(status_text)
                
        elif d['status'] == 'finished':
            self.status_signal.emit("Download finished, processing file...")
    
    def cancel(self):
        if self._running:
            self._running = False
            self.status_signal.emit("Cancelling download...")