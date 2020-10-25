import psycopg2
from flask import Flask, request
from flask_cors import CORS
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

app = Flask(__name__)  # create a flask app
cors = CORS(app)


def dbConnect():
    print('DB connect: ', end='')
    try:
        connection = psycopg2.connect(
            "dbname='d34ct5fc6m9li0' user='epebpvfyedbkvc' host='ec2-54-246-85-151.eu-west-1.compute.amazonaws.com' password='9f9418d9f3857783f122b36f92b79ce39a7ae3257e2b397e61fd5965a1aabb1f'")
        print('OK')
        cursor = connection.cursor()
        return connection, cursor
    except:
        print("Coudln't connect to the database.\n")


def dbDisconnect(connection, cursor):
    connection.close()
    cursor.close()
    return


def printDB(cursor):
    cursor.execute("SELECT * FROM USERCREDENTIALS")
    allData = cursor.fetchall()
    for data in allData:
        print(data)


@app.route('/verify', methods=['POST', 'GET'])
def verifyLogIn():
    incomingData = request.get_json()

    username = incomingData['username']
    password = incomingData['password']
    connection, cursor = dbConnect()
    cursor.execute("CREATE TABLE IF NOT EXISTS USERCREDENTIALS(USERNAME VARCHAR, PASSWORD_HASHED VARCHAR, SALT BYTEA)")
    cursor.execute("SELECT PASSWORD_HASHED, SALT from USERCREDENTIALS where USERNAME=%s", (username,))
    dbData = cursor.fetchall()
    if not dbData:
        return 'incorrect name or username', 404

    salt = dbData[0][1]
    hashedPasswordFromDB = dbData[0][0]
    saltedPassword = password.encode() + salt
    hash = SHA256.new()
    hash.update(saltedPassword)
    if hashedPasswordFromDB == hash.hexdigest():
        dbDisconnect(connection, cursor)
        return 'server: ok', 201
    else:
        dbDisconnect(connection, cursor)
        return 'incorrect name or username', 404


@app.route('/register', methods=['POST'])
def registerUser():
    incomingData = request.get_json()

    username = incomingData['username']
    password = incomingData['password']
    salt = get_random_bytes(32)

    saltedPassword = password.encode() + salt
    hash = SHA256.new()
    hash.update(saltedPassword)

    connection, cursor = dbConnect()
    # cursor.execute("DROP TABLE USERCREDENTIALS")
    cursor.execute("CREATE TABLE IF NOT EXISTS USERCREDENTIALS(USERNAME VARCHAR, PASSWORD_HASHED VARCHAR, SALT BYTEA)")
    cursor.execute("SELECT USERNAME from USERCREDENTIALS where USERNAME=%s", (username,))
    if cursor.fetchone() is not None:
        return 'name already exists', 404

    cursor.execute("INSERT INTO USERCREDENTIALS(USERNAME, PASSWORD_HASHED, SALT) VALUES (%s, %s, %s)",(username, hash.hexdigest(), salt))
    connection.commit()

    dbDisconnect(connection, cursor)
    return 'server: ok', 201


if __name__ == '__main__':
    app.run(threaded=False, processes=1)
