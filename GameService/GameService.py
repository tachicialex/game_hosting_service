from flask import Flask, request, Response
from jsonrpcserver import method, dispatch
import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import sys

app = Flask(__name__)

db_name = "gamedb"
database_host = "database"

@method
def login_player(name):
	# check if player is new:
	db = connection.MySQLConnection(host=database_host, user="root", password="root", database=db_name)
	cursor = db.cursor()

	sql = "SELECT username, score FROM Users WHERE username='%s'" % name
	cursor.execute(sql)

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

@app.route("/", methods=["POST"])
def index():
	req = request.get_data().decode()
	response = dispatch(req)
	return Response(str(response), response.http_status, mimetype="application/json")

if __name__ == "__main__":
	

	# listen on rpc json port:
	app.run(host='0.0.0.0', port=7549, debug=True)
