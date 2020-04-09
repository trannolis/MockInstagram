#Import Flask Library
from flask import Flask, flash, render_template, request, session, url_for, redirect
import pymysql.cursors
import os
from datetime import datetime

from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = '/Users/nicktran/Documents/GitHub/MockInstagram/UPLOAD_FOLDER'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#Initialize the app from Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/select_user')
def select_user():
    #check that user is logged in
    username = session['username']
    #should throw exception if username not found
    cursor = conn.cursor();
    query = 'SELECT DISTINCT followee FROM Follow WHERE follower = %s AND followStatus=1'
    #query = 'SELECT DISTINCT username FROM BelongTo NATURAL JOIN Follow'
    cursor.execute(query,username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_user.html', user_list=data)

@app.route('/show_posts', methods=["GET", "POST"])
def show_posts():
    poster = request.args['poster']
    cursor = conn.cursor();
    query = 'SELECT postingDate, pID FROM Photo WHERE poster = %s ORDER BY postingDate DESC'
    cursor.execute(query, poster)
    data = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', poster_name=poster, posts=data)

@app.route('/followUser', methods=["GET", "POST"])
def followUser():
    user = session['username']
    user_to_follow = request.form['followUser']
    cursor = conn.cursor();
    query = 'SELECT follower, followee FROM follower WHERE follower = %s AND followee = %s'
    cursor.execute(query, user_to_follow)
    data = cursor.fetchone()
    if(data):
        query = 'UPDATE follow SET followStatus = 1 WHERE follower = %s AND followee = %s'
        cursor.execute(query, (user, user_to_follow))
    else:
        query = 'INSERT INTO follower VALUES(%s %s 1)'
        cursor.execute(query, user_to_follow)
    cursor.close()
    return render_template('show_posts.html', poster_name=user_to_follow, posts=data)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods = ['GET','POST'])
def upload():
    username = session['username']

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            caption = request.form['caption']
            public = request.form.getlist('shareTo')
            try:
                if not public:
                    public.append(0)
            finally:
                print("error in try-catch")

            postingDate = datetime.now()

            cursor = conn.cursor()
            sql_insertPhoto = """ INSERT INTO Photo
                          (postingDate, filePath, allFollowers, caption, poster) VALUES (%s,%s,%s,%s,%s)"""

            sql_insertTuple = postingDate, filename, public[0], caption, username
            cursor.execute(sql_insertPhoto, sql_insertTuple)
            conn.commit()

            print("Sucessfully uploaded a photo for: " + username)
            return redirect(url_for('home'))

    return redirect(url_for('home'))

app.secret_key = 'some key that you will never guess'

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
