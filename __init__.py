#!/usr/bin/python3
from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database_setup import Base, Genre, Book
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client import client
from oauth2client.client import FlowExchangeError
from flask import make_response
import httplib2
import json
import random
import string
import requests
import os
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.debug = True
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
path = os.path.dirname(__file__)
CLIENT_ID = json.loads(
    open('/var/www/App/itemCatalog/client_secrets.json', 'r').read())['web']['client_id']
CLIENT_SECRET_FILE = '/var/www/App/itemCatalog/client_secrets.json'


def checkUser():
    ''' Checks if user is logged in. '''
    return 'username' in login_session


@app.errorhandler(404)
def not_found(error):
    ''' if 404 error redirect to custom 404 page'''
    return render_template("404.html")


@app.route('/login')
def showLogin():
    '''handling login
    make sure user get log in if it is not
    or check if it is already exit and redirects to home
    Args:
        None

    Returns:
        redirects to Main page if already logged in
        redirects to login.html if not logged in
    '''
    if 'username' in login_session:
        return redirect(url_for('bookStoreMain'))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/logout')
def showLogout():
    '''  handling logout

    Args:
        None

    Returns:
        redirects to gdisconnect to revoke google token
        redirects to home if no user not logged in
    '''
    if 'username' in login_session:
        return redirect(url_for('gdisconnect'))
    else:
        flash("No user logged in")
        return redirect(url_for("bookStoreMain"))

# check gconnect for any problems
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
        code)
    gplus_id = credentials.id_token['sub']
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;:'
    output += '"-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])

    # revoke token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)

    # if successfully revoked delete session data
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you have disconnected successfully")
        return redirect(url_for('bookStoreMain'))
    else:
        failed = 'Failed to revoke token for given user.'
        response = make_response(json.dumps(failed), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/bookstore/')
def bookStoreMain():
    '''  show Main page
    retrive all genres and the first 5 books added
    and checks for user if logged in to show name and logout

    Args:
        None

    Returns:
        redirects to home page (bookstore.html)
    '''
    genres = session.query(Genre)
    books = session.query(Book).order_by(Book.id.desc()).limit(5)
    user = login_session['username'] if checkUser() else 'None'
    return render_template('bookstore.html', genres=genres,
                           user=user, books=books)


@app.route('/bookstore/<string:genre_name>/')
def genreBooks(genre_name):
    '''  show Books in genre
    retrive books from database which belongs to genre
    Args:
        string:genre_name

    Returns:
        render (genreBooks.html) using genre, its books
            and username if exists
    '''
    user = login_session['username'] if checkUser() else 'None'
    genre = session.query(Genre).filter_by(name=genre_name).one()
    books = session.query(Book).filter_by(genre_id=genre.id)
    return render_template('genreBooks.html',
                           genre=genre,
                           books=books,
                           user=user)


@app.route('/bookstore/<int:genre_id>/<int:book_id>/')
def viewBook(genre_id, book_id):
    '''  show Book details
    Args:
        int:genre_id
        int:book_id

    Returns:
        render (viewBook.html) using genre and book
            and username if exists
    '''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    book = session.query(Book).filter_by(genre_id=genre.id,
                                         id=book_id).one()
    user = login_session['username'] if checkUser() else 'None'
    return render_template('viewBook.html',
                           book=book,
                           genre=genre,
                           user=user)


@app.route('/bookstore/<string:genre_name>/book/new', methods=['GET', 'POST'])
def newBook(genre_name):
    '''  Handling adding new book
    Checks if users is logged becuase only users allowed to add new books
    if post retrive data from the form and saves to data

    Args:
        string:genre_name

    Raises:
        IntegrityError : if the new book has duplicate data with book in db

    Returns:
        POST: render (genreBooks.html) after submiting data
        GET: render (newBook.html)
    '''
    user = login_session['username'] if checkUser() else 'None'
    if user != 'None':
        genre = session.query(Genre).filter_by(name=genre_name).one()
        if request.method == 'POST':
            # collecting data recieved from the form
            name_book = request.form['name']
            desc_book = request.form['description']
            price_book = request.form['price']
            isbn_book = request.form['isbn']
            author_book = request.form['author']
            num_book = request.form['numberOfPages']

            newBookItem = Book(name=name_book, description=desc_book,
                               author=author_book, price=price_book,
                               isbn=isbn_book, numberOfPages=num_book,
                               created_by_name=user,
                               created_by_email=login_session['email'],
                               genre_id=genre.id)
            # Check if Error occured during adding new book
            try:
                session.add(newBookItem)
                session.commit()
                flash('New book added')
            except IntegrityError:
                session.rollback()
                flash('something went wrong please check the data you entered')
            return redirect(url_for('genreBooks',
                                    genre_name=genre_name,
                                    user=user))
        else:
            return render_template('newBook.html',
                                   genre_name=genre_name,
                                   user=user)
    # if no user is logged
    else:
        flash("you have to login first to add new book")
        return redirect(url_for('showLogin'))


@app.route('/bookstore/<string:genre_name>/book/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(genre_name, book_id):
    '''  Handling editing book
    Checks if users is logged becuase only users allowed to edit books
    if post retrive changed fields from the form and saves to database

    Args:
        string:genre_name
        int:book_id

    Raises:
        IntegrityError : if edited book data has duplicate data
                         with  another book in db

    Returns:
        POST: render (genreBooks.html) after submiting data
        GET: render (editBook.html)
    '''
    user = login_session['username'] if checkUser() else 'None'
    if user != 'None':
        genre = session.query(Genre).filter_by(name=genre_name).one()
        bookToBeEdited = session.query(Book).filter_by(id=book_id).one()

        if login_session['email'] != bookToBeEdited.created_by_email:
            flash("you can't edit it because someone else created it")
            return redirect(url_for('genreBooks', genre_name=genre.name,
                                    user=user))
        if request.method == 'POST':
            if request.form['name']:
                bookToBeEdited.name = request.form['name']
            if request.form['description']:
                bookToBeEdited.description = request.form['description']
            if request.form['price']:
                bookToBeEdited.price = request.form['price']
            if request.form['numberOfPages']:
                bookToBeEdited.numberOfPages = request.form['numberOfPages']
            if request.form['author']:
                bookToBeEdited.author = request.form['author']
            # Check if Error occured during editing book
            try:
                session.add(bookToBeEdited)
                session.commit()
                flash("Edited successfully")
            except IntegrityError:
                session.rollback()
                flash('something went wrong please check the data entered')
            return redirect(url_for('genreBooks', genre_name=genre_name,
                                    user=user))
        else:
            return render_template('editBook.html',
                                   genre=genre,
                                   book=bookToBeEdited,
                                   user=user)
    # if no user is logged
    else:
        flash("you have to login first to edit a book")
        return redirect(url_for('showLogin'))

@app.route('/bookstore/<string:genre_name>/book/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(genre_name, book_id):
    '''  Handling delete book
    Checks if users is logged becuase only users allowed to edit books
    Confirms if user wants to delete the book

    Args:
        string:genre_name
        int:book_id

    Returns:
        POSt: render (genreBooks.html) after submiting data
        GET: render (deleteconfirmationBook.html)
    '''
    user = login_session['username'] if checkUser() else 'None'
    if user != 'None':
        book = session.query(Book).filter_by(id=book_id).one()
        genre = session.query(Genre).filter_by(name=genre_name).one()
        if login_session['email'] != book.created_by_email:
            flash("you can't delete it because someone else created it")
            return redirect(url_for('genreBooks', genre_name=genre.name,
                                    user=user))
        if request.method == "POST":
            session.delete(book)
            session.commit()
            flash('Book Successfully Deleted')
            return redirect(url_for('genreBooks', genre_name=genre.name,
                                    user=user))
        else:
            return render_template('deleteBookConfirmation.html', genre=genre,
                                   book=book)
    # if no user is logged
    else:
        flash('you have to login first to delete a book')
        return redirect(url_for('showLogin'))


@app.route('/bookstore/<int:genre_id>/JSON')
def genreJSON(genre_id):
    ''' Returns JSON for the genre and all its books'''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    books = session.query(Book).filter_by(genre_id=genre_id).all()
    return jsonify(Genre=genre.name, Books=[i.serialize for i in books])


@app.route('/bookstore/<int:genre_id>/<int:book_id>/JSON')
def bookJSON(genre_id, book_id):
    ''' Returns JSON form for specific book with its genre'''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    book = session.query(Book).filter_by(genre_id=genre_id, id=book_id).one()
    return jsonify(Genre=genre.name, Book=book.serialize)


if __name__ == '__main__':
    app.secret_key = 'Secret Key'
    app.run()
