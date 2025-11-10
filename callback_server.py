from flask import Flask, request
import threading
import time
import os

app = Flask(__name__)
auth_code_file = 'auth_code.txt'  # File to store the auth code

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    if auth_code:
        with open(auth_code_file, 'w') as f:
            f.write(auth_code)
        print(f"DEBUG: Received and saved auth code: {auth_code}")
    return "Auth code received. You can close this window."

def run_server():
    app.run(host='0.0.0.0', port=8080)

# Start server in a separate thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

print("DEBUG: Callback server started on http://localhost:8080. Waiting for redirect...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("DEBUG: Shutting down server.")
    if os.path.exists(auth_code_file):
        os.remove(auth_code_file)  # Clean up file on exit