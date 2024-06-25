# IP Widget

IP Widget is a Windows Python application that displays the current IP address location as a system tray icon.

Features:

- Shows current IP address location.
- Option to run at startup.
- System tray menu for easy access.

Screenshots:

![Screenshot of IP Widget tray icon](https://github.com/IPS277L/ip-widget/blob/main/screenshots/ip-widget-tray.png)
![Screenshot of IP Widget tray icon menu](https://github.com/IPS277L/ip-widget/blob/main/screenshots/ip-widget-tray-menu.png)

# Local installation

Requirements:
- Operating System: Windows 11 (not tested with older versions).
- Python Version: 3.x.
- Version Control: Git.

Clone the repository and navigate into the project directory:
```bash
git clone https://github.com/IPS277L/ip-widget.git
cd ip-widget
```

Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

Execute the main Python script:
```bash
python main.py
```

Run the build command:
```bash
python setup.py build
```

# Download

You can download the latest release or portable version of IP Widget from [GitHub Releases page](https://github.com/IPS277L/ip-widget/releases).
