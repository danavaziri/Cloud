import os
import time

from flask import request
from flask import Flask, render_template
import mysql.connector
from mysql.connector import errorcode
import json


application = Flask(__name__)
app = application


def get_db_creds():
    db = os.environ.get("DB", None) or os.environ.get("database", None)
    username = os.environ.get("USER", None) or os.environ.get("username", None)
    password = os.environ.get("PASSWORD", None) or os.environ.get("password", None)
    hostname = os.environ.get("HOST", None) or os.environ.get("dbhost", None)
    return db, username, password, hostname


def create_table():
    # Check if table exists or not. Create and populate it only if it does not exist.
    db, username, password, hostname = get_db_creds()
    table_ddl = 'CREATE TABLE movies(id INT UNSIGNED NOT NULL AUTO_INCREMENT, year INT, title TEXT, director TEXT, actor TEXT, release_date TEXT, rating FLOAT, PRIMARY KEY (id))'

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        #try:
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)
        #except Exception as exp1:
        #    print(exp1)

    cur = cnx.cursor()

    try:
        cur.execute(table_ddl)
        cnx.commit()
        populate_data()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)


def populate_data():

    db, username, password, hostname = get_db_creds()

    print("Inside populate_data")
    print("DB: %s" % db)
    print("Username: %s" % username)
    print("Password: %s" % password)
    print("Hostname: %s" % hostname)

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                       host=hostname,
                                       database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()
    cur.execute("INSERT INTO message (greeting) values ('Hello, World!')")
    cnx.commit()
    print("Returning from populate_data")


def query_data():

    db, username, password, hostname = get_db_creds()

    print("Inside query_data")
    print("DB: %s" % db)
    print("Username: %s" % username)
    print("Password: %s" % password)
    print("Hostname: %s" % hostname)

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()

    cur.execute("SELECT greeting FROM message")
    entries = [dict(greeting=row[0]) for row in cur.fetchall()]
    return entries

try:
    print("---------" + time.strftime('%a %H:%M:%S'))
    print("Before create_table global")
    create_table()
    print("After create_data global")
except Exception as exp:
    print("Got exception %s" % exp)
    conn = None




######### INSERT/UPDATE MOVIE #########
@app.route('/add_to_db', methods=['POST'])
def add_to_db():
    print("Received request.")
    print(request.form['year'])
    year = request.form['year']
    title = request.form['title']
    actor = request.form['actor']
    director = request.form['director']
    release_date = request.form['release_date']
    rating = request.form['rating']

    actor = actor.title()
    director = director.title()

    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()

    cur.execute("SELECT id FROM movies WHERE LOWER(title) = ('" + title.lower() + "')")
    print("CHECK TO SEE IF  UPDATEE!!!!!!")
    entries = [dict(id=row[0]) for row in cur.fetchall()]
    if not entries:
        cur.execute("INSERT INTO movies (year, title, director, actor, release_date, rating) values ('" + year + "','" + title + "','" + director + "','" + actor + "','" + release_date + "','" + rating + "')")
        try:
            cnx.commit()
        except Exception as exp:
            return add_movie_print(exp)
        return add_movie_print("Movie " + title + " successfully inserted")




######### DELETE MOVIE #########
@app.route('/delete_movie', methods=['POST'])
def delete_movie():
    print("Received DELETE request.")
    print(request.form['delete_movie_box'])
    msg = request.form['delete_movie_box']
    lower_title = msg.lower()

    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()

    cur.execute("SELECT title FROM movies WHERE LOWER(title) = ('" + lower_title + "')")
    entries = [dict(title=row[0]) for row in cur.fetchall()]
    if not entries:
        return delete_movie_print("Movie " + msg + " could not be deleted - Movie with " + msg + " does not exist")

    cur2 = cnx.cursor()

    cur2.execute("DELETE FROM movies WHERE (title) =  ('" + msg + "')")
    try:
        cnx.commit()
    except Exception as exp:
        return delete_movie_print(exp)
    return delete_movie_print("Movie " + msg + " successfully deleted")




######### SEARCH MOVIE #########
@app.route('/search_movie', methods=['POST'])
def search_movie():
    print("Received SEARCH request.")
    print(request.form['search_actor_box'])
    msg = request.form['search_actor_box']
    msg = msg.title()

    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()

    cur.execute("SELECT title FROM movies WHERE actor = ('" + msg + "')")
    entries = [dict(title=row[0]) for row in cur.fetchall()]
    if not entries:
        failed = "No movies found for actor " + msg
        return print_search_movie(entries, failed)

    cur.execute("SELECT year, title, actor FROM movies WHERE actor = ('" + msg + "')")
    entries = [dict(year=row[0], title=row[1], actor=row[2]) for row in cur.fetchall()]
    json_data = json.dumps(entries)
    s = "" + str(json_data)
    s = s[1:]
    s = s[:-1]
    s = s[1:]
    s = s[:-1]
    result = s.split("}, {")
    return print_search_movie(result, "")




######### PRINT HIGHEST RATING MOVIES #########
@app.route('/print_movie_highest', methods=['POST'])
def print_movie_highest():
    print("Received PRINT HIGH request.")

    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()
    cur.execute("SELECT year, title, director, actor, rating FROM movies WHERE rating=(SELECT MAX(rating) FROM movies)")
    entries = [dict(rating=row[4], actor=row[3], director=row[2], title=row[1], year=row[0]) for row in cur.fetchall()]
    json_data = json.dumps(entries)
    s = "" + str(json_data)
    s = s[1:]
    s = s[:-1]
    s = s[1:]
    s = s[:-1]
    result = s.split("}, {")
    return print_highest_stat_movie(result)

######### PRINT HIGHEST RATING MOVIES #########
@app.route('/print_movie_lowest', methods=['POST'])
def print_movie_lowest():
    print("Received PRINT LOW request.")

    db, username, password, hostname = get_db_creds()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db)

    cur = cnx.cursor()
    cur.execute("SELECT year, title, director, actor, rating FROM movies WHERE rating=(SELECT MIN(rating) FROM movies)")
    entries = [dict(rating=row[4], actor=row[3], director=row[2], title=row[1], year=row[0]) for row in cur.fetchall()]
    json_data = json.dumps(entries)
    s = "" + str(json_data)
    s = s[1:]
    s = s[:-1]
    s = s[1:]
    s = s[:-1]
    result = s.split("}, {")
    return print_lowest_stat_movie(result)






@app.route("/")
def hello():
    print("Inside hello")
    print("Printing available environment variables")
    print(os.environ)
    print("Before displaying index.html")
    entries = query_data()
    print("Entries: %s" % entries)
    return render_template('index.html', entries=entries)


def add_movie_print(message):
    print("Printing searched movies")
    print("Before displaying searched movies in index.html")
    print("Searched Movies: %s" % message)
    return render_template('index.html', insert_msg=message)

def delete_movie_print(message):
    print("Printing searched movies")
    print("Before displaying searched movies in index.html")
    print("Searched Movies: %s" % message)
    return render_template('index.html', delete_msg=message)

def print_search_movie(searched_movies, failed_msg):
    print("Printing searched movies")
    print("Before displaying searched movies in index.html")
    print("Searched Movies: %s" % searched_movies)
    if failed_msg != "":
        return render_template('index.html', movies_searched_fail=failed_msg)
    return render_template('index.html', movies_searched=searched_movies)

def print_highest_stat_movie(movie_stat):
    print("Printing movies STATS")
    print("Before displaying stats of movies in index.html")
    print("Searched Movies: %s" % movie_stat)
    return render_template('index.html', highest_rating_movies=movie_stat)

def print_lowest_stat_movie(movie_stat):
    print("Printing movies STATS")
    print("Before displaying stats of movies in index.html")
    print("Searched Movies: %s" % movie_stat)
    return render_template('index.html', lowest_rating_movies=movie_stat)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
