from flask import Flask, request, Response
from jsonrpcserver import method, dispatch
import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import sys

app = Flask(__name__)

db_name = "gamedb"
database_host = "database"

available_lobbies = ["gamelobby"]
running_lobbies = []

class Lobby:
	def __init__(self, username, host_name):
		self.username = username
		self.nr_players = 1
		self.host_name = host_name
	def get_list(self):
		return [self.username, self.nr_players, self.host_name]

@method
def login_player(name):
	# check if player is new:
	db = connection.MySQLConnection(host=database_host, user="root", password="root", database=db_name)
	cursor = db.cursor()

	sql = "SELECT username, score FROM Users WHERE username='%s'" % name
	cursor.execute(sql)

	# check if user exists here
	users = cursor.fetchall()
	if (len(users) == 0):
		# register new user:
		sql = "INSERT INTO Users VALUES('%s', 0)" % name
		cursor = db.cursor()

		cursor.execute(sql)
		db.commit()
		db.close()
		return "Welcome %s!" % name
	else:
		# return current score to user:
		user_data = users[0]

		db.close()
		return "Welcome back %s [score %d]" % (user_data[0], int(user_data[1]))

@method
def create_lobby(username):
	if len(available_lobbies) == 0:
		return "Not Available."
	else:
		host_name = available_lobbies.pop()
		running_lobbies.append(Lobby(username, host_name))
		return host_name

@method
def get_lobbies():
	lobbies_list = []
	for lobby in running_lobbies:
		lobbies_list.append(lobby.get_list())
	return str(lobbies_list)

@app.route("/", methods=["POST"])
def index():
	req = request.get_data().decode()
	response = dispatch(req)
	return Response(str(response), response.http_status, mimetype="application/json")

if __name__ == "__main__":
	

	# listen on rpc json port:
	app.run(host='0.0.0.0', port=7549, debug=True)
