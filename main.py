import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/login')
def login():
    return flask.render_template('login.html')

if __name__ == "__main__":
    # change name for testing
    app.run(debug=True, host="0.0.0.0", port="8454")