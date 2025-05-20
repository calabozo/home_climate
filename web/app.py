from air_vent import open_vent, close_vent
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/air_vent/open/<int:vent_id>')
def open_air_vent(vent_id):
    # Call the open_vent() function with the provided vent_id
    open_vent(vent_id)
    # Return a message to indicate success
    return f"Opened air vent {vent_id}"


@app.route('/air_vent/close/<int:vent_id>')
def close_air_vent(vent_id):
    # Call the close_vent() function with the provided vent_id
    close_vent(vent_id)
    # Return a message to indicate success
    return f"Closed air vent {vent_id}"


if __name__ == '__main__':
    app.run(debug=True)

