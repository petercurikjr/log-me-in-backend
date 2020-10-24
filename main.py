import psycopg2
from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__) #create a flask app

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def verifyLogIn():
    incomingData = request.get_json()
    username = incomingData['username']
    password = incomingData['password']
    return 'ok', 201

if __name__ == '__main__':
    app.run(threaded=False, processes=1)
