from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlsplit, parse_qs
import db
import ems
import json
import csv

PORT_NUMBER = 8080
LOG_FILE = 'logfile.txt'
DB_FILE = 'pwhash.txt'




class BookrServer(HTTPServer):
	def __init__(self, url, handler):
		super().__init__(url, handler)
		f = open(LOG_FILE, 'w')
		self.logfile = f
		f = open(DB_FILE, 'r')
		self.passwords = f
		with open(DB_FILE) as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    self.db, self.tokenized_db = db.csv_to_dict(reader)
		    self.logfile.write(str(self.db) + "\n")

	def cleanup(self):
		self.logfile.close()
		self.passwords.close()

def list_to_json(lst):
	new_lst = []
	for item in lst:
		tmp = {"name": item[0],"capacity": item[1]}
		new_lst.append(tmp)
	return {"rooms": new_lst}

#This class will handles any incoming request from
#the browser 
class BookrHandler(BaseHTTPRequestHandler):
	
	def verify_user(self, token):
		result = self.server.tokenized_db.get(token)
		return result != None

	def room_request(self, params):

		keys = ["st", "et", "dt", 
			"cpty", "t"]

		all_info = True
		for key in keys:
			if (not params.get(key)):
				all_info = False

		if all_info:
			if not self.verify_user(params['t'][0]):
			    return "invalid-user"
			rooms = ems.get_rooms(params['dt'][0], params['st'][0], 
					params['et'][0],
					params['cpty'][0] )

			if len(rooms):
				rooms = list_to_json(rooms)
				return json.dumps(rooms)
			else:
				return "no-rooms-available"

		else:
			return "not-enough-info"
	def do_login(self, params):

		# Retrieve given username and hashed password
		username = params['u'][0]
		password = params['p'][0]

		# Authenticate
		success = 'Invalid'
		token   = 'NULL'

		entry = self.server.db.get(username)
		self.server.logfile.write(username + "\n")
		if entry:
			stored_pw = entry[0]
			stored_token = entry[1]
			if password == stored_pw:
				success = 'Valid'
				token = stored_token
			else:
				self.server.logfile.write("Actual hash: " +
					stored_pw + ", Given hash: " + password)


		# Return token or report invalid login
		response = json.dumps({"success": success, "token": token})
		self.wfile.write(bytes(response, 'utf-8'))

	def do_room_request(self, params):
		result = self.room_request(params)
		self.wfile.write(bytes(result, 'utf-8'))

	def do_booking(self, params):
		start_time = params['st'][0]
		end_time   = params['et'][0]
		date       = params['dt'][0]
		name       = params['n'][0]

		result = ems.create_reservation(date, start_time, end_time, name)
		self.wfile.write(bytes(result, 'utf-8'))
		
	def get_booking(self, params):
		eventId = params['id'][0]

		response = json.dumps({"valid": "valid", "room": "default"})
		self.wfile.write(bytes(response, 'utf-8'))

	#Handler for the GET requests
	def do_POST(self):
		parsed = urlsplit(self.path)
		path = parsed[2] or '//'
		path = path.rstrip('/')

		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.data_string = self.rfile.read(int(self.headers['Content-Length']))
		self.end_headers()

		# Send the html message
		data = self.data_string.decode('utf-8')
		self.server.logfile.write(str(data) + "\n")
		params = parse_qs(str(data))
		
		if path == "/request-room": 
			self.do_room_request(params)
		elif path == "/auth":
		        self.do_login(params)
		elif path == "/book-room":
			self.do_booking(params)                
		elif path == "/booking":
			self.get_booking(params)
		else:
			result = "invalid-request"
			self.wfile.write(bytes(result, 'utf-8'))

		self.server.logfile.write("Received POST request \n")
		return

	def do_GET(self):
		parsed = urlsplit(self.path)
		path = parsed[2] or '//'
		path = path.rstrip('/')
		params = parse_qs(parsed.query)

		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.end_headers()
		# Send the html message
		
		if path == "/request-room": 
			result = room_request(params)
		else:
			result = "Invalid request"
		self.wfile.write(bytes(result, 'utf-8'))
		self.server.logfile.write("received POST request")
		return

#try:
#Create a web server and define the handler to manage the
#incoming request
server = BookrServer(('', PORT_NUMBER), BookrHandler)
print('Started httpserver on port ' , PORT_NUMBER)

#Wait forever for incoming htto requests
server.serve_forever()

#except KeyboardInterrupt:
#	print('^C received, shutting down the web server')
#	server.socket.close()
#	server.cleanup()
