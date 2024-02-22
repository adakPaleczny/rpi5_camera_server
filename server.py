from flask import Flask, Response
import cv2

from camera_recognition.camera_vision import VisionCamera  # Ensure this import works correctly

app = Flask(__name__)
pi_camera = VisionCamera()  # Ensure the camera is initialized correctly here

USE_MODEL = False

@app.route('/')
def index():
    # HTML template for the index page with a link to the live video page
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Feed</title>
    </head>
    <body>
        <input type="text" id="username" name="username"><br><br>
        <input type="password" id="password" name="password"><br><br>
        <input type="submit" value="Login">
        <h1>Welcome to the Live Camera Feed</h1>
        <p>Click <a href="/video">here</a> to view the live video stream.</p>
    </body>

    <script>
        function log(){
            l = document.getElementById('username');
            p = document.getElementById('password');
        }
    </script>
    </html>
    """
    return html

def gen(pi_cam):
    """Video streaming generator function."""
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
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.10.1', port=8080, debug=False)
