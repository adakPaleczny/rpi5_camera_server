from flask import Flask, Response, render_template, request, redirect, session
import cv2
import sqlite3
from camera_recognition.camera_vision import VisionCamera  # Ensure this import works correctly

app = Flask(__name__)
pi_camera = VisionCamera()  # Ensure the camera is initialized correctly here

app.secret_key = '692137_papierz'  # Set to a random string

@app.route('/', methods=["GET","POST"])
def index():
    # HTML template for the index page with a link to the live video page
    if request.method == "POST":
        user = request.form.get('username')
        password = request.form.get('password')
        
        # return f'{user}, your username is {password}'
        db = sqlite3.connect("database/data.db")
        cur = db.cursor()
        res = cur.execute("SELECT user_id FROM osoby WHERE login = ? AND pass = ?", (user, password)).fetchone()
        if(res):
            session['is_authorized'] = True
            return redirect('/video')
        else:
            return f'No authorization'
    session['is_authorized'] = False
    return render_template('index.html')

def gen(pi_cam):
    # """Video streaming generator function."""
    while True:
        success, image = pi_cam.camera.read()
        if not success:
            break  # If there's an error reading, exit the loop
      
        image = pi_cam.runModel(image)
        
        ret, buffer = cv2.imencode('.jpg', image)
        if ret:
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video')
def video():
    # """Video streaming route. Put this in the src attribute of an img tag."""
    if not session.get('is_authorized', False):
        return redirect("/")

    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.10.1', port=8080, debug=False)
