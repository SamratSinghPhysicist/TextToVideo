import os
import threading
import time
from flask import Flask
from main import process_video  # Assuming process_video is the function that runs your tasks

app = Flask(__name__)

@app.route("/")
def home():
    return "App is running and scheduled tasks are executing."

def run_scheduled_tasks():
    # This function runs your main video processing tasks.
    # Replace the following with your actual scheduling loop, e.g., schedule.run_pending()
    while True:
        print("Running scheduled tasks...")
        process_video()  # or call your scheduled process function
        time.sleep(60 * 60)  # wait an hour before the next run; adjust as needed

if __name__ == "__main__":
    # Start the scheduled tasks in a background thread
    task_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    task_thread.start()

    # Bind to the port provided by Render (defaults to 5000 if not set)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
