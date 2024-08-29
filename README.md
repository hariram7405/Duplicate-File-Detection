# Download Monitor and Duplicate Detector

This project monitors a specified download directory for new files, detects duplicate files based on their SHA-256 hash, and prompts the user with a warning box if a duplicate is found. The system uses `watchdog` to monitor file creation and `sqlite3` to keep a record of downloaded files.

## Features

- Monitors a specified download directory for new files.
- Calculates SHA-256 hashes for new files to detect duplicates.
- Uses SQLite to store download history.
- Prompts the user with a Tkinter message box if a duplicate file is detected, allowing them to choose whether to delete the duplicate or keep it.

## Installation

### Prerequisites

Ensure you have Python 3 installed. You can download it from [python.org](https://www.python.org/downloads/).

### Dependencies

You will need to install the following Python packages:

- `watchdog`
- `tkinter` (usually included with Python installations)

You can install the required packages using pip:

```bash
pip install watchdog
