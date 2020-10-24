import psycopg2
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__) #create a flask app
cors = CORS(app) #enables javascript to interact with this server. for more, see enable-cors.org/server_flask.html

@app.route('/', methods=['POST', 'GET'])
def verifyLogIn():
    incomingData = request.get_json()
    username = incomingData['username']
    password = incomingData['password']
    return 'ok', 201

if __name__ == '__main__':
    app.run(threaded=False, processes=1)
