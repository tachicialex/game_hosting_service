from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from jsonrpcclient.clients.http_client import HTTPClient
import sys

from flask_login import LoginManager, UserMixin, \
login_required, login_user, logout_user
from flask_login import current_user
import pickle
import socket

UDP_IP = "gamelobby"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

client = 0
app = Flask(__name__)
app.secret_key = b'_asfsfsad\n\xec]/'
login_manager = LoginManager()

logged_users = {}

class User(UserMixin):
	def __init__(self, id):
		self.id = id
		self.name = str(id)
		self.password = self.name + "_secret"
		self.game_matrix = [['-', '-', '-'],['-', '-', '-'],['-', '-', '-']]

	def get_id(self):
		return self.id

	def is_active(self):
		return True
	def is_authenticated(self):
		return True

@login_manager.user_loader
def load_user(user_id):
	if user_id in logged_users:
		return logged_users[user_id]
	else:
		return None

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

		user = User(username)
		logged_users[username] = user
		login_user(user)
		return options(username, str(response.result))
	return render_template('login.html')

@app.route("/lobby", methods=['GET', 'POST'])
@login_required
def lobby():
	if request.method == 'POST':
		print("User selected: " + request.form['submit_button'])
		clicked_position = eval(request.form['submit_button'])

		# send move data to the lobby:
		data = pickle.dumps(["move", current_user.id, clicked_position])
		sock.sendto(data, (UDP_IP, UDP_PORT))

	# ask for gamestate:
	data = pickle.dumps(["state", current_user.id])
	sock.sendto(data, (UDP_IP, UDP_PORT))

	# receive game data from the lobby:
	# game_data = [game_matrix, players, game_status, player turn]
	data, addr = sock.recvfrom(1024)
	game_data = pickle.loads(data)

	# check if game ended:
	if game_data[2][0]:
		# game ended:
		# send disconect req:
		data = pickle.dumps(["disconnect", current_user.id, (0,0)])
		sock.sendto(data, (UDP_IP, UDP_PORT))

		return options(current_user.id, game_data[2][1] + " Won!")

	current_user.game_matrix = game_data[0]
	player_names_chars = []
	for player_name in game_data[1]:
		player_names_chars.append((player_name, game_data[1][player_name]))

	return render_template(
		'lobby.html',
		game_matrix=current_user.game_matrix,
		player=current_user.id,
		player_turn=game_data[3],
		players=player_names_chars
		)

# redirect to lobby page
@app.route("/createlobby")
@login_required
def pressed_create_lobby():
	username = current_user.id
	# return lobby host name:
	response = client.create_lobby(username).data
	print(response) 
	UDP_IP = str(response.result)


	return redirect(url_for('lobby'))

# redirect game lists page
@app.route("/lobbies", methods=['GET', 'POST'])
@login_required
def list_lobbies():

	# get lobbies running from server:
	response = client.get_lobbies().data
	print(response) 
	running_lobbies = eval(response.result)

	if request.method == 'POST':
		clicked_lobby_name = request.form['submit_button']
		print(clicked_lobby_name)

		# get host name for the selected lobby:
		for lobby in running_lobbies:
			if lobby[0] == clicked_lobby_name:
				UDP_IP = lobby[2]
				return redirect(url_for('lobby'))

	# running_lobby = [name, nr players, host_name]
	return render_template('lobbies.html',lobbies_list=running_lobbies)

# redirect game lists page
@app.route("/findlobby")
@login_required
def pressed_find_lobby():

	return redirect(url_for('list_lobbies'))

# options page:
@app.route("/options")
@login_required
def options(username, server_message):
	return render_template('options.html', username=username, server_message=server_message)

# game page:

if __name__ == "__main__":
	# connect to the game server:
	client = HTTPClient(server_host)
	login_manager.init_app(app)
	app.run(debug=True, host="0.0.0.0")