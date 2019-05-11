import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import sys
import socket
import pickle

db_name = "gamedb"
database_host = "database"

UDP_IP = "0.0.0.0"
UDP_PORT = 5005


game_matrix = [['-', '-', '-'],['-', '-', '-'],['-', '-', '-']]
game_started = False

# key: player name
# value: string 'X' or 'O'
players = {}
current_player_turn = ""
first_player = ""
second_player = ""

player_turn = ""
game_finished = ""
game_status = (False, None)

def reset_game():
	game_finished = ""
	game_status = (False, None)
	for i in range(3):
		for j in range(3):
			game_matrix[i][j] = '-'

def get_player_with_char(player_char):
	for player_name in players.keys():
		if players[player_name] == player_char:
			return player_name
	return None

# returns (True, Player_name)
def check_if_game_finished():
	player_char = ""

	# check rows:
	for i in range(3):
		player_char = game_matrix[i][0]
		player_char_won = True
		for j in range(3):
			if game_matrix[i][j] == '-':
				player_char_won = False
			if player_char != game_matrix[i][j]:
				player_char_won = False
		if player_char_won:
			player_with_char = get_player_with_char(player_char)
			return (True, player_with_char)

	#check columns:
	for i in range(3):
		player_char = game_matrix[0][i]
		player_char_won = True
		for j in range(3):
			if game_matrix[j][i] == '-':
				player_char_won = False
			if player_char != game_matrix[j][i]:
				player_char_won = False
		if player_char_won:
			player_with_char = get_player_with_char(player_char)
			return (True, player_with_char)

	# check axis:
	if game_matrix[0][0] == game_matrix[1][1] == game_matrix[2][2] and game_matrix[1][1] != '-':
		return (True, get_player_with_char(game_matrix[0][0]))
	
	if game_matrix[2][0] == game_matrix[1][1] == game_matrix[0][2] and game_matrix[1][1] != '-':
		return (True, get_player_with_char(game_matrix[2][0]))

	return (False, None)

def run_game():

	global game_matrix
	global game_started

	# key: player name
	# value: string 'X' or 'O'
	global players
	global current_player_turn
	global first_player
	global second_player

	global player_turn
	global game_finished
	global game_status

	# wait for move:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, UDP_PORT))

	while True:
		data, addr = sock.recvfrom(200)
		
		# req = [request, user name, clicked position] 
		req = pickle.loads(data)

		# add user to dict:
		if len(players.keys()) == 0:
			# first users gets 'X'
			players[req[1]] = 'X'
			first_player = req[1]
			player_turn = first_player
			game_started = False

		elif len(players.keys()) == 1 and req[1] not in players:
			# second player gets 'O'
			players[req[1]] = 'O'
			second_player = req[1]
			# start the game:
			game_started = True

		if req[0] == "move" and game_started and player_turn == req[1]:
			move = req[2]
			print("received message: " + str(req) + " (from: " + str(addr) + ")")
			# apply move to the matrix if empty:
			if game_matrix[move[0]][move[1]] == '-':
				game_matrix[move[0]][move[1]] = players[req[1]]
				# next player moves:
				if player_turn == first_player:
					player_turn = second_player
				else:
					player_turn = first_player

		if game_started and not game_status[0]:
			game_status = check_if_game_finished()

		# send new game state to client
		if req[0] == "state":
			game_data = [game_matrix, players, game_status, player_turn]
			data = pickle.dumps(game_data)
			sock.sendto(data, addr)

		if req[0] == "disconnect":
			# remove player:
			players.pop(req[1], None)

			if len(players.keys()) == 0:
				# all players disconnected:

				# increment score to winner:
				db = connection.MySQLConnection(host=database_host, user="root", password="root", database=db_name)
				cursor = db.cursor()
				sql = "UPDATE Users SET score=score+1 WHERE username='%s'" % game_status[1]
				print(sql)
				cursor.execute(sql)

				db.commit()
				db.close()

				# reset lobby:
				game_matrix = [['-', '-', '-'],['-', '-', '-'],['-', '-', '-']]
				game_started = False

				# key: player name
				# value: string 'X' or 'O'
				players = {}
				current_player_turn = ""
				first_player = ""
				second_player = ""

				player_turn = ""
				game_finished = ""
				game_status = (False, None)
				break

	sock.close()

if __name__ == "__main__":
	
	while True:
		run_game()
