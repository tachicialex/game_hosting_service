from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from jsonrpcclient.clients.http_client import HTTPClient
import sys

client = 0
app = Flask(__name__)

server_host = "http://gameservice:7549"

@app.route("/")
def home():
	return redirect(url_for('login'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		print("User %s tried login." % username)

		# send login request to game server:
		response = client.login_player(username).data
		print(response)
		return options(username, str(response.result))
	return render_template('login.html')

# options page:
@app.route("/options")
def options(username, server_message):
	return render_template('options.html', username=username, server_message=server_message)

# game page:

if __name__ == "__main__":
	# connect to the game server:
	client = HTTPClient(server_host)
	app.run(debug=True, host="0.0.0.0")