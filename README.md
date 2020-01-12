# Item Catalog Project #

## Description ##

Bookstore contains books organized by genres, you can login to create/edit/delete books.
Every book has details that can be created from :
- Name **required**
- ISBN **required**
- Number of pages
- Author
- Price

## links ##
- Bookstore main
- Genre books
- View book detail
- Create new book **require login**
- Edit book **require login**
- Delete book **require login**
- login
- logout
- Genre JSON ***displays JSON form of genre with its books***
- Book JSON ***displays JSON form of single book with its genre***

## Requirment ##
- python 3
- sqlalchemy
- oauth2client
- flask
- httplib2

## How to run ##
1. Run in console `pip install flask oauth2client flask-httpauth sqlalchemy flask-sqlalchemy httplib2`
2. Run in console `python freshData.py`
3. Run in console`python project.py`
4. In browser go to http://localhost:3000/
