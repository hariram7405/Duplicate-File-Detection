import os
import time
import hashlib
import sqlite3
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from tkinter import Tk, messagebox

# Set the default download location
DOWNLOAD_DIR = r'C:\Users\ADMIN\Downloads'

# Create a database connection
conn = sqlite3.connect('download_history.db')
cursor = conn.cursor()

# Create a table to store download history
cursor.execute('''
CREATE TABLE IF NOT EXISTS download_history
(file_hash TEXT PRIMARY KEY, file_name TEXT, file_size INTEGER, download_time TEXT)
''')

# Create a queue to pass file hashes from the watchdog thread to the main thread
file_hash_queue = queue.Queue()

# Create a queue to pass messages from the thread to the main thread
message_queue = queue.Queue()

class MonitorDownloads(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the event is a file creation
        if not event.is_directory:
            # Get the file path and name
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            # Ignore temporary files
            if file_name.endswith('.tmp'):
                return
            # Wait for the file to finish downloading
            while True:
                try:
                    # Try to get the file size
                    file_size = os.path.getsize(file_path)
                    # If successful, break the loop
                    break
                except OSError:
                    # If the file is still being written, wait for 1 second
                    time.sleep(1)
            # Calculate the file's hash
            file_hash = self.calculate_file_hash(file_path)
            # Put the file hash and path in the queue
            file_hash_queue.put((file_hash, file_path))
            print(f"Processing file: {file_name}")

    def calculate_file_hash(self, file_path):
        # Calculate the file's hash using SHA-256
        with open(file_path, 'rb') as file:
            file_hash = hashlib.sha256()
            while True:
                chunk = file.read(8192)
                if not chunk:
                    break
                file_hash.update(chunk)
        return file_hash.hexdigest()

def process_file_hashes(root):
    conn = sqlite3.connect('download_history.db')
    cursor = conn.cursor()
    while True:
        file_hash, file_path = file_hash_queue.get()
        # Check if the file has already been downloaded
        cursor.execute('SELECT * FROM download_history WHERE file_hash = ?', (file_hash,))
        existing_download = cursor.fetchone()
        if existing_download:
            print(f"Duplicate file found: {existing_download[1]}")
            # Put the message in the queue
            message_queue.put(f"Duplicate file found: {existing_download[1]}")
        else:
            # Add the file to the download history
            cursor.execute('INSERT INTO download_history VALUES (?, ?, ?, ?)', (file_hash, os.path.basename(file_path), os.path.getsize(file_path), time.ctime()))
            conn.commit()
            print(f"New file downloaded: {os.path.basename(file_path)}")
        print("Ongoing process...")

def main():
    # Create an event handler
    event_handler = MonitorDownloads()
    # Create an observer
    observer = Observer()
    # Set the observer to monitor the download directory
    observer.schedule(event_handler, path=DOWNLOAD_DIR, recursive=False)
    # Start the observer
    observer.start()
    # Create a Tk instance for the message box
    root = Tk()
    root.withdraw()
    # Start a new thread to process file hashes
    threading.Thread(target=process_file_hashes, args=(root,)).start()
    try:
        while True:
            # Sleep for 1 second
            time.sleep(1)
            print("Monitoring downloads...")
            # Check the message queue
            try:
                message = message_queue.get(block=False)
                messagebox.showwarning("Duplicate File", message, parent=root)
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        # Stop the observer
        observer.stop()
    observer.join()
    conn.close()

if __name__ == "__main__":
    main()
