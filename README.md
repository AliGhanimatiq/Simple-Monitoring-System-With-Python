# System Monitor

Real-time system monitoring tool for Windows

![Screenshot](screenshot.png)

## Features
- CPU/RAM/Disk monitoring
- Network latency tracking
- Portable executable
- Dark theme

## Download
Get the latest release from [Releases page](https://github.com/yourusername/yourrepo/releases)

## Build from Source
```bash
pip install -r requirements.txt
pyinstaller --onefile --noconsole --hidden-import="pynput.keyboard._win32" --collect-data matplotlib --collect-data psutil system_monitor.py
