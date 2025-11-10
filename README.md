# TrueCall App

TrueCall is a hackathon demo application for simulating and verifying branded business calls using Kivy (Python GUI framework). It demonstrates how verified business calls can be presented to users with branding, video intros, and caller information. The app also integrates with APIs and AI utilities for enhanced features.

## Features
- Simulate incoming verified business calls with branding
- Display business name, logo, video intro, and phone numbers
- Popup notification for dramatic incoming call effect
- AI-powered location description (via LLM)
- Callback server for OAuth authentication
- Configurable via `config.ini`

## Files
- `truecall_app.py`: Main Kivy application for TrueCall
- `truecall_simulation.py`: Demo simulation of branded business calls
- `callback_server.py`: Flask server to handle OAuth callback and save auth code
- `config.ini`: API keys and configuration
- `requirements.txt`: Python dependencies
- `rules.txt`: Test instructions and phone number ranges

## Getting Started

### Prerequisites
- Python 3.8+
- Install dependencies:
  ```powershell
  pip install -r requirements.txt
  ```

### Running the App
1. Start the callback server (for OAuth):
   ```powershell
   python callback_server.py
   ```
2. Run the TrueCall Kivy app:
   ```powershell
   python truecall_app.py
   ```
   Or run the simulation demo:
   ```powershell
   python truecall_simulation.py
   ```

### Testing
- Use phone numbers in the range `+61400500800` to `+61400500999` for API testing (see `rules.txt`).

## Configuration
- Edit `config.ini` to set API keys and other settings.

## License
This project is for hackathon/demo purposes only.
