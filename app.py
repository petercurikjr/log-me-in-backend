import psycopg2
from flask import Flask, request
from flask_cors import CORS
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

# create a flask app
app = Flask(__name__)
# allow incoming requests
cors = CORS(app)

#establish a connection with db
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

#close a connection with db
def dbDisconnect(connection, cursor):
    connection.close()
    cursor.close()
    return

#print contents of db
def printDB(cursor):
    cursor.execute("SELECT * FROM USERCREDENTIALS")
    allData = cursor.fetchall()
    for data in allData:
        print(data)

#do this function when URL has https://...../verify
@app.route('/verify', methods=['POST', 'GET'])
def verifyLogIn():
    #process the incoming data
    incomingData = request.get_json()
    username = incomingData['username']
    password = incomingData['password']

    #connect to the db
    connection, cursor = dbConnect()
    #create a new table if it doesnt exist yet
    cursor.execute("CREATE TABLE IF NOT EXISTS USERCREDENTIALS(USERNAME VARCHAR, PASSWORD_HASHED VARCHAR, SALT BYTEA)")
    #find all users with given username
    cursor.execute("SELECT PASSWORD_HASHED, SALT from USERCREDENTIALS where USERNAME=%s", (username,))
    #dbData contains the result of the db query
    dbData = cursor.fetchall()
    #if no user was found - login fails - incorrect username
    if not dbData:
        return 'incorrect name or username', 404

    #get salt from dbData (which contains obtained data from the db query)
    salt = dbData[0][1]
    #get hashed password from dbData (which contains obtained data from the db query)
    hashedPasswordFromDB = dbData[0][0]
    #add the salt from the db to the password obtained from the website
    saltedPassword = password.encode() + salt
    #hash it
    hash = SHA256.new()
    hash.update(saltedPassword)

    #and finally compare hash of password from the website with a hash of password from the db
    if hashedPasswordFromDB == hash.hexdigest():
        #disconnect from the db first, then send response back to the website
        dbDisconnect(connection, cursor)
        return 'server: ok', 201
    else:
        #disconnect from the db first, then send response back to the website
        dbDisconnect(connection, cursor)
        #hashes are not equal - which means the password from the website is wrong
        return 'incorrect name or username', 404

#do this function when URL has https://...../register
@app.route('/register', methods=['POST'])
def registerUser():
    #process the incoming data
    incomingData = request.get_json()
    username = incomingData['username']
    password = incomingData['password']

    #generate salt with true random generator (128 bits)
    salt = get_random_bytes(32)

    #add salt to the password received from the website
    saltedPassword = password.encode() + salt
    #hash it
    hash = SHA256.new()
    hash.update(saltedPassword)

    #connect to the db
    connection, cursor = dbConnect()
    #create a new table if it doesnt exist yet
    cursor.execute("CREATE TABLE IF NOT EXISTS USERCREDENTIALS(USERNAME VARCHAR, PASSWORD_HASHED VARCHAR, SALT BYTEA)")
    #find all users with given username
    cursor.execute("SELECT USERNAME from USERCREDENTIALS where USERNAME=%s", (username,))
    #when query result is not empty - user is already registered with that username - return error
    if cursor.fetchone() is not None:
        return 'name already exists', 404

    #insert a row to the db with given username, password (hashed) and salt
    cursor.execute("INSERT INTO USERCREDENTIALS(USERNAME, PASSWORD_HASHED, SALT) VALUES (%s, %s, %s)",(username, hash.hexdigest(), salt))
    connection.commit()

    #disconnect from the db first, then send response back to the website
    dbDisconnect(connection, cursor)
    return 'server: ok', 201


if __name__ == '__main__':
    app.run(threaded=False, processes=1)
