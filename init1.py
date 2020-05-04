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
                       port = 3308,
                       user='root',
                       password='',
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
    query = """SELECT pID, postingDate, filePath, firstName,lastName FROM 
    Photo AS p1 JOIN person AS pe ON(p1.poster=pe.username) WHERE 
    p1.poster = %s OR p1.pID IN(SELECT pID FROM follow AS f JOIN Photo AS p2 
    ON(f.followee=p2.poster) WHERE f.followStatus=1 AND p2.AllFollowers=1 AND 
    f.follower = %s) OR p1.pID IN (SELECT pID from belongto as b JOIN sharedwith 
    AS s USING(groupName, groupCreator) WHERE b.username = %s) ORDER BY 
    postingDate DESC"""
    cursor.execute(query, (user,user,user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)

@app.route('/select_user')
def select_user():
    #check that user is logged in
    username = session['username']
    #should throw exception if username not found
    cursor = conn.cursor()
    query = 'SELECT DISTINCT followee FROM Follow WHERE follower = %s AND followStatus=1'
    #query = 'SELECT DISTINCT username FROM BelongTo NATURAL JOIN Follow'
    cursor.execute(query,username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_user.html', user_list=data)

@app.route('/show_posts', methods=["GET", "POST"])
def show_posts():
    poster = request.args['poster']
    cursor = conn.cursor()
    query = 'SELECT postingDate, pID FROM Photo WHERE poster = %s ORDER BY postingDate DESC'
    cursor.execute(query, poster)
    data = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', poster_name=poster, posts=data)

@app.route('/follow_user', methods=["GET", "POST"])
def follow_user():
    user = session['username']
    user_to_follow = request.form['followUser']
    cursor = conn.cursor()
    query = 'SELECT * FROM follow WHERE follower = %s AND followee = %s'
    cursor.execute(query, (user, user_to_follow))
    data = cursor.fetchone()
    if(data):
        return render_template('addFriendFailure.html') # you are already friends with this person or pending response
    ins = 'INSERT INTO follow VALUES(%s, %s, 0)'
    cursor.execute(ins, (user, user_to_follow))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/inbox', methods = ['GET'])
def inbox():
    username = session['username']
    cursor = conn.cursor()
    query = "SELECT follower FROM Follow WHERE followee = %s AND followStatus = 0"
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('inbox.html', requests=data)

@app.route('/respond', methods = ["GET"])
def respond():
    username = session['username']
    reqFriend = request.args['requester']
    accept = request.args['Accept']
    cursor = conn.cursor()
    if accept == "Accept":
        query1 = 'UPDATE Follow SET followStatus = 1 WHERE follower = %s AND followee = %s'
        cursor.execute(query1, (reqFriend, username))
    else:
        query2 = 'DELETE FROM Follow WHERE follower = %s AND followee = %s'
        cursor.execute(query2, (reqFriend, username))
    conn.commit()
    query3 = "SELECT follower FROM Follow WHERE followee = %s AND followStatus = 0"
    cursor.execute(query3, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('inbox.html', requests = data)

@app.route('/createFriendGroup', methods=["GET", "POST"])
def createFriendGroup():
    user = session['username']
    reqGroupName = request.form['createFG']
    reqDescr = request.form['descrFG']
    cursor = conn.cursor()
    query = 'SELECT * FROM FriendGroup WHERE FriendGroup.groupName = %s AND FriendGroup.groupCreator = %s'
    cursor.execute(query, (reqGroupName,user))
    data = cursor.fetchone()
    if(data):
        cursor.close()
        return render_template('friendGroupError.html')
    else:
        ins = 'INSERT INTO FriendGroup VALUES(%s, %s, %s)'
        cursor.execute(ins, (reqGroupName, user, reqDescr))
        conn.commit()
        ins = 'INSERT INTO belongto VALUES(%s, %s, %s)'
        cursor.execute(ins, (user, reqGroupName, user))
        conn.commit()
    cursor.close()
    return redirect(url_for('home'))

#Extra Feature 1 - Nick Tran
@app.route('/selectFG')
def selectFG():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT DISTINCT groupName FROM FriendGroup WHERE groupCreator = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('selectFG.html', user_list=data)

#Extra Feature 1 - Nick Tran
@app.route('/addFriend', methods = ["GET", "POST"])
def addFriend():
    username = session['username']
    reqFriend = request.args['friend']
    groupName = request.args['friendGroups'] #gets selected groupName
    if username == reqFriend:
        return render_template("friendError2.html")
    cursor = conn.cursor()
    query = 'SELECT * FROM Person WHERE Person.username = %s' #checks if they exist
    cursor.execute(query, reqFriend)
    data = cursor.fetchall()
    if(data):
        #check if they aren't already in the group
        query1 = 'SELECT * FROM BelongTo WHERE BelongTo.username = %s AND BelongTo.groupName = %s'
        cursor.execute(query1, (reqFriend, groupName))
        check = cursor.fetchall()
        if(check):
            cursor.close()
            return render_template("friendError.html") #the person is already in the group
        else:
            ins = 'INSERT INTO BelongTo VALUES (%s, %s, %s)'
            cursor.execute(ins, (reqFriend, groupName, username))
            conn.commit()
    cursor.close()
    return render_template('success.html', groupName = groupName)

#Extra Feature 2 - Nick Tran
@app.route('/analyze', methods = ['GET','POST'])
def analyze():
    username = session['username']
    cursor = conn.cursor()
    #finding number of followers per person
    query = 'SELECT followee, count(followStatus) as numFollowers FROM Follow WHERE followstatus = 1 GROUP BY followee ORDER BY numFollowers desc'
    cursor.execute(query)
    data = cursor.fetchall()
    #finding most-reacted to photos
    query2 = """SELECT DISTINCT pID, count(pID) as numReactions FROM reactto WHERE 
            pID IN (SELECT pID FROM photo AS p NATURAL JOIN follow AS f WHERE 
            p.allFollowers=1 AND f.follower= %s AND f.followee = p.poster AND 
            f.followStatus = 1) OR pID IN (SELECT pID FROM sharedwith AS s NATURAL 
            JOIN belongto AS b WHERE s.groupName = b.groupName AND s.groupCreator = 
            b.groupCreator AND b.username = %s)
            GROUP BY pID ORDER BY numReactions desc LIMIT 10"""
    cursor.execute(query2, (username, username))
    data2 = cursor.fetchall()
    cursor.close()
    return render_template('analytics.html', followList=data, reactPhotos=data2)

#Extra Feature 3 - Faizan Hussain

@app.route('/unfollow_user', methods=["GET", "POST"])
def unfollow_user():
    user = session['username']
    user_to_unfollow = request.form['unfollowUser']
    cursor = conn.cursor()
    query = 'SELECT * FROM follow WHERE follower = %s AND followee = %s AND followStatus = 1'
    cursor.execute(query, (user, user_to_unfollow))
    data = cursor.fetchone()
    if(not data):
        return render_template('unfollowFailure.html') # you aren't already following this person, and can't unfollow them,
    ins = 'DELETE FROM follow WHERE follower = %s and followee =%s'
    cursor.execute(ins, (user, user_to_unfollow))
    conn.commit()
    query = """SELECT pID FROM tag as t WHERE t.username = %s AND t.pID IN(SELECT pID 
    FROM Photo AS p WHERE p.poster = %s) AND t.pID NOT IN (SELECT pID FROM 
    sharedwith AS s JOIN belongto AS b USING(groupName,groupCreator) 
    WHERE b.username= %s)"""
    cursor.execute(query, (user, user_to_unfollow, user))
    data = cursor.fetchone()
    if(data):
        ins = """DELETE FROM tag as t WHERE t.username = %s AND t.pID IN(SELECT pID 
        FROM Photo AS p WHERE p.poster = %s) AND t.pID NOT IN (SELECT pID FROM 
        sharedwith AS s JOIN belongto AS b USING(groupName,groupCreator) 
        WHERE b.username= %s)"""
        cursor.execute(ins, (user, user_to_unfollow,user))
        conn.commit()
    cursor.close()
    return redirect(url_for('home'))

#Extra Feature 4 - Faizan Hussain

@app.route('/setTags', methods=["GET", "POST"])
def setTags():
    user = session['username']
    reqpID = request.form['idPhoto']
    reqTag = request.form['tagPhoto']
    cursor = conn.cursor();
    query = """SELECT pID FROM photo As p0 WHERE p0.pID= %s AND p0.pID IN (SELECT pID FROM Photo AS p1 WHERE 
    p1.poster = %s OR p1.pID IN(SELECT pID FROM follow AS f JOIN Photo AS p2 
    ON(f.followee=p2.poster) WHERE f.followStatus=1 AND p2.AllFollowers=1 AND 
    f.follower = %s) OR p1.pID IN (SELECT pID from belongto as b JOIN sharedwith 
    AS s USING(groupName, groupCreator) WHERE b.username = %s))"""
    cursor.execute(query, (str(reqpID),user,user,user))
    data = cursor.fetchone()
    if(not data):
        return render_template('setTagsFailure.html')
    if(reqTag==user):
        ins = 'INSERT INTO tag VALUES(%s, %s, 1)'
        cursor.execute(ins, (str(reqpID),user))
    else:
        query = """SELECT pID FROM photo As p0 WHERE p0.pID= %s AND p0.pID IN (SELECT pID FROM Photo AS p1 WHERE 
        p1.poster = %s OR p1.pID IN(SELECT pID FROM follow AS f JOIN Photo AS p2 
        ON(f.followee=p2.poster) WHERE f.followStatus=1 AND p2.AllFollowers=1 AND 
        f.follower = %s) OR p1.pID IN (SELECT pID from belongto as b JOIN sharedwith 
        AS s USING(groupName, groupCreator) WHERE b.username = %s))"""
        cursor.execute(query, (str(reqpID),reqTag,reqTag,reqTag))
        data = cursor.fetchone()
        if(data):
            ins = 'INSERT INTO tag VALUES(%s, %s, 0)'
            cursor.execute(ins, (str(reqpID),reqTag))
        else:
            return render_template('setTagsFailure.html')
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/proposedTags', methods = ['GET'])
def proposedTags():
    username = session['username']
    cursor = conn.cursor()
    query = "SELECT pID FROM tag WHERE username = %s AND tagStatus = 0"
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('proposedTags.html', requests=data)

@app.route('/respondToTags', methods = ["GET"])
def respondToTags():
    user = session['username']
    reqpID = request.args['idPhoto']
    accept = request.args['Accept']
    cursor = conn.cursor()
    if accept == "Accept":
        query1 = 'UPDATE tag SET tagStatus = 1 WHERE username = %s AND pID = %s'
        cursor.execute(query1, (user, str(reqpID)))
        print('Updated Tagged Person: ' + user + " Photo: " + reqpID)
    else:
        print('deleting ' + user + ' tag from photo ' + reqpID)
        query2 = 'DELETE FROM tag WHERE username = %s AND pID = %s'
        cursor.execute(query2, (user, str(reqpID)))
    conn.commit()
    query3 = "SELECT pID FROM tag WHERE username = %s AND tagStatus = 0"
    cursor.execute(query3, user)
    data = cursor.fetchall()
    cursor.close()
    return render_template('proposedTags.html', requests = data)

#Extra Feature 5 - Tommy Gao, search tagged users
@app.route('/search_tag', methods=["GET", "POST"])
def search_tag():
    user = session['username']
    user_to_searchTag = request.form['searchTag']
    cursor = conn.cursor()
    query = """SELECT pID FROM tag WHERE username = %s AND tagStatus > 0 AND 
    (pID IN (SELECT pID FROM photo AS p NATURAL JOIN follow AS f WHERE 
    p.allFollowers=1 AND f.follower= %s AND f.followee = p.poster AND 
    f.followStatus = 1) OR pID IN (SELECT pID FROM sharedwith AS s NATURAL JOIN 
    belongto AS b WHERE s.groupName = b.groupName AND s.groupCreator = 
    b.groupCreator AND b.username = %s))"""
    cursor.execute(query, (user_to_searchTag, user, user))
    data = cursor.fetchall()
    if(data):
        query = """SELECT pID FROM tag WHERE username = %s AND tagStatus > 0 AND 
            (pID IN (SELECT pID FROM photo AS p NATURAL JOIN follow AS f WHERE 
            p.allFollowers=1 AND f.follower= %s AND f.followee = p.poster AND 
            f.followStatus = 1) OR pID IN (SELECT pID FROM sharedwith AS s NATURAL JOIN 
            belongto AS b WHERE s.groupName = b.groupName AND s.groupCreator = 
            b.groupCreator AND b.username = %s))"""
        cursor.execute(query, (user_to_searchTag, user, user))
        data = cursor.fetchall()
        cursor.close()
        return render_template('show_tag.html', taggedName=user_to_searchTag, posts=data)
    else:
        return render_template('noTags.html')  # Nothing found or no permission to view

#Extra Feature 6 - Tommy Gao, react to a photo
@app.route('/reacts', methods=["GET", "POST"])  # shows reactions
def react():
    # check that user is logged in
    username = session['username']
    postID = request.args['reactPost']

    cursor = conn.cursor()
    query = 'SELECT DISTINCT pID, username, reactionTime, comment, emoji FROM reactto WHERE pID = %s'
    cursor.execute(query, postID)
    data = cursor.fetchall()
    cursor.close()
    return render_template('reacts.html', postID=postID, reactions=data)

# react yourself
@app.route('/reacting', methods=["GET", "POST"])
def reacting():
    # check that user is logged in
    username = session['username']
    postID = request.args['reactPost']
    emoji = request.args['reaction']
    comm = request.args['comment']
    reactingDate = datetime.now()
    cursor = conn.cursor()
    query = 'SELECT username FROM reactto WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    if(data):
        dele = 'DELETE FROM reactto WHERE username = %s'
        cursor.execute(dele, (username))

    ins = 'INSERT INTO reactto VALUES(%s, %s, %s, %s, %s)'
    cursor.execute(ins, (username, postID, reactingDate, comm, emoji))
    query = 'SELECT pID, reactionTime, comment, emoji FROM reactto WHERE pID = %s'
    cursor.execute(query, postID)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template('reacting.html', postID=postID, reactions=data)
      
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

@app.route('/sharePhoto', methods=["GET", "POST"])
def sharePhoto():
    user = session['username']
    reqpID = request.form['idPhoto']
    reqGroupName = request.form['gName']
    reqGroupCreator = request.form['gCreator']
    cursor = conn.cursor();
    query = """SELECT pID FROM photo As p0 WHERE p0.pID= %s AND p0.poster= %s"""
    cursor.execute(query, (str(reqpID),user))
    data = cursor.fetchone()
    if(not data):
        return render_template('sharePhotoFailure1.html')
    query = """SELECT pID FROM sharedwith WHERE pID = %s"""
    cursor.execute(query,str(reqpID))
    data = cursor.fetchone()
    if(data):
        return render_template('sharePhotoFailure2.html')
    query = """SELECT username FROM belongTo WHERE username = %s AND groupName = %s AND groupCreator= %s"""
    cursor.execute(query,(user,reqGroupName,reqGroupCreator))
    data = cursor.fetchone()
    if(not data):
        return render_template('sharePhotoFailure3.html')
    else:
        query = """INSERT INTO sharedwith VALUES(%s, %s, %s)"""
        cursor.execute(query, (str(reqpID),reqGroupName,reqGroupCreator))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))
  
app.secret_key = 'some key that you will never guess'

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
