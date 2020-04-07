#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

import mysql.connector
from mysql.connector import Error

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='mockinstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstname, lastname, email))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/home')
def home():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT postingDate, filePath FROM Photo WHERE poster = %s ORDER BY postingDate DESC'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)


    """
    @app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor();
    blog = request.form['blog']
    query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
    cursor.execute(query, (blog, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))
    """


@app.route('/select_blogger')
def select_blogger():
    #check that user is logged in
    #username = session['username']
    #should throw exception if username not found
    
    cursor = conn.cursor();
    query = 'SELECT DISTINCT username FROM blog'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_blogger.html', user_list=data)

@app.route('/show_posts', methods=["GET", "POST"])
def show_posts():
    poster = request.args['poster']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, poster)
    data = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', poster_name=poster, posts=data)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def insertBLOB(username, photo):
    print("Inserting BLOB into photo table")

    username = request.form['username']
    postingDate = request.form['postingDate']
    allFollowers = request.form['allFollowers']
    caption = request.form['caption']

    #   Just to clarify since you specify that the table auto increments photoIDs
    #   You do not have to insert into that column since that will be done for you.

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='mockinstagram',
                                             user='root',
                                             password='root')

        cursor = connection.cursor()

        sql_insert_blob_query = """ INSERT INTO Photo
                          (postingDate, filePath, allFollowers, caption, poster) VALUES (%s,%s,%s,%s,%s)"""

        photo = convertToBinaryData(photo)

        # Convert data into tuple format
        insert_blob_tuple = (postingDate, photo, allFollowers, caption, username)
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        print("Image and file inserted successfully as a BLOB into Photos table", result)

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

################################################################
# Retrieving Image and File stored as a BLOB from MySQL Table
################################################################

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

def readBLOB(photoId, photo):
    print("Reading BLOB data from Photo table")

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='mockinstagram',
                                             user='root',
                                             password='root')

        cursor = connection.cursor()
        sql_fetch_blob_query = """SELECT photo from Photo where id = %s"""

        cursor.execute(sql_fetch_blob_query, (photoId,))
        record = cursor.fetchall()
        for row in record:
            print("photoID = ", row[0], )
            image = row[1]
            print("Storing photo on disk \n")
            write_file(image, photo)

    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


@app.route('/upload', methods = ['POST'])
def upload():
    user = session['username']
    upfile = request.files['inputFile']
    insertBLOB(username=user, photo=upfile)

    return "success!" + redirect(url_for('home'))

app.secret_key = 'some key that you will never guess'

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
