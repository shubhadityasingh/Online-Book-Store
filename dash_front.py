from flask import Flask, render_template, redirect, url_for,request
import json
import pandas as pd
import numpy as nppip
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy import create_engine
import mysql.connector
from mysql import connector
from psycopg2 import sql
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime # Current date time in local system print(datetime.now())
from datetime import date
from datetime import time
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/mealplan'

db = SQLAlchemy(app)


from flask import Flask, render_template, redirect, url_for,request, flash
import os
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, DateField, ValidationError
from wtforms.validators import InputRequired, Email, Length, DataRequired, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import jsonify
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/information'
# app.config['TESTING'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    _cart = db.Column(db.String, default = '0')
    _orders = db.Column(db.String, default = '0')
    sales = db.Column(db.Integer, default = 0)
    total_rating = db.Column(db.Integer, default = 0)
    # _rating = db.Column(db.String, default = '0')


    def get_reset_token(self, expires_sec = 1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')


    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            #s.loads(token)['user_id'] = None
        except:
            return None
        return User.query.get(user_id)
    
    @property
    def cart(self):
        return [int(x) for x in self._cart.split('-')]

    @cart.setter
    def cart(self, value):
        self._cart += '-%s' %value

    def empty_cart(self):
        self._cart = '0'


    def reset(self, new_cart):
        self._cart = new_cart

    
    @property
    def orders(self):
        return [int(x) for x in self._orders.split('-')]

    @orders.setter
    def orders(self, value):
        self._orders += '-%s' %value



    def __repr__(self):
        return f"User('{self.id}','{self.username}', '{self.email}', '{self.cart}')"





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me?')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username = username.data).first()
    #     if user is False:
    #         raise ValidationError('This username does not exist. Please try again.', 'danger')
    
    # def validate_password(self, password):
    #     user = User.query.filter_by(username = username.data).first()
    #     if user:
    #         if check_password_hash(user.password, password.data) is False:
    #             raise ValidationError('Wrong Password. Please try again.', 'danger')




class RegisterForm(FlaskForm):
    dob=DateField('Date of Birth', format='%m/%d/%Y')
    gender=StringField('Gender', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.', 'danger')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('This email is already taken. Please choose a different one.', 'danger')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    # submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must first create an account.')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # submit = SubmitField('Reset Password')




class books(db.Model):
    #  = db.Column(db.String(80))
    id = db.Column(db.Integer(),primary_key=True)
    book_name = db.Column(db.String(80))
    price = db.Column(db.String(20),nullable=True)


    image=db.Column(db.String(80),nullable=True)
    details=db.Column(db.String(2000),nullable=False)


    author = db.Column(db.String(80),nullable=True)
    date_upload = db.Column(db.String(80),nullable=True)
    seller_id = db.Column(db.Integer(),nullable=True)



    def __repr__(self):
        return f"books('{self.book_name}', '{self.author}')"
    



class buy_log(db.Model):
    #  = db.Column(db.String(80))
    id = db.Column(db.Integer(),primary_key=True)

    customer_name=db.Column(db.String(80),nullable=True)
    customer_number=db.Column(db.String(80),nullable=True)
    customer_address=db.Column(db.String(80),nullable=True)

    book_name = db.Column(db.String(80))
    price = db.Column(db.String(20),nullable=True)
    details=db.Column(db.String(2000),nullable=False)
    author = db.Column(db.String(80),nullable=True)
    image=db.Column(db.String(80),nullable=True)
    date_upload = db.Column(db.String(80),nullable=True)

    date_sold = db.Column(db.String(80),nullable=True)
    rating = db.Column(db.Integer(),nullable=True)
    seller_id = db.Column(db.Integer(),nullable=True)





def add_book(the_book_name,the_price,the_image,the_details,the_author):
    info=books()
    info.book_name=the_book_name
    info.price=the_price
    info.image=the_image
    info.details=the_details
    info.author=the_author
    info.seller_id = current_user.id

    getdate = date.today()
    info.date_upload=datetime.now()
 
 
    db.session.add(info)
    db.session.commit()
    




def delete_book(the_book_name,the_price,the_image,the_details,the_author):


    print("\n\nYOOO:\n\n",the_book_name)
    print("\n\nYOOO:\n\n",the_details)
    cnx = mysql.connector.connect(user='root', database='information')
    cursor = cnx.cursor()

    

    
    query = """DELETE FROM books WHERE (book_name = '"""+str(the_book_name)+"""' ) AND (details = '"""+str(the_details)+"""' ) ; """

    cursor.execute(query)
    
    
    cnx.commit() 
    cursor.close()
    cnx.close()




    

def add_buy_log(book,customer_name,customer_number,customer_address):
    info=buy_log()
    
    info.book_name=book.book_name
    info.price=book.price
    info.details=book.details
    info.image=book.image
    info.author=book.author
    info.seller_id = book.seller_id
    info.rating = 0
    # info.buyer_id = current_user.id



    info.customer_name=customer_name
    info.customer_number=customer_number
    info.customer_address=customer_address

    
    info.date_upload =book.date_upload

    info.date_sold =datetime.now()




 
    db.session.add(info)
    db.session.commit()
    return info.id



db.create_all()



#add_book("20th century boys","830","https://images-na.ssl-images-amazon.com/images/I/91F15VTNFFL.jpg","gud bouk","Naoki Urasawa")


#oke so boi, rn you made the cards to show products and also made a stupid funtion to add those new books to the database, now u gotta
#1. make a form in accounts to upload book info through this function (refer myrecipies.html)
#2. link these cards of books to the product_page.html, again refer myrecipies.html, u might need to use button and form shit, glhf lol
#3. idk but running that function makes shit add twice, probably cause of cmd running shit twice, nvm that, ignore it


@app.route('/grahil')
def grahil():
    return render_template('grahil.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            
            userr=current_user.username
            


            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check your username and password and try again.', 'danger')

    return render_template('login_new.html', form=form)
        # return render_template('recipe.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()


        


        return render_template('index.html', form=form)
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup_new.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#~~~~~~~~~~~        OPENS MAIN DASHBOARD PAGE               ~~~~~~~~~~~~~~~~~~~~~~
@app.route('/')
def index():
    return render_template('index.html')




@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    #~~~~~~~~~~~~~~ for featured products ~~~~~~~~~~~~~~
    cnx = mysql.connector.connect(user='root', database='information')
    cursor = cnx.cursor()

    

    
    query2 = """ SELECT image, book_name, price FROM books """



    cursor.execute(query2)
    result=cursor.fetchall()

    


    #print("\n\n\nall books: \n",result)

    #print("\n\n\nrandomed: \n",random.sample(result, 4))
    result_imporved=random.sample(result, 4)

    re=[]
    re2=[]
    re3=[]


    for x in result_imporved:
        #print("\n\nkinda nice i gues: \n",x)
        re.append(x[0])
        re2.append(x[1])
        re3.append(x[2])

    #print("\n\n\nall books in nice form \n",re)
    

    #print("\n\n\nhelloooooo2:  \n   ",re2)
    #print("\n\n\nprice:   \n  ",re3)



    cursor.close()
    cnx.close()






    #~~~~~~~~~~~~~~ for latest products ~~~~~~~~~~~~~~

    cnx = mysql.connector.connect(user='root', database='information')
    cursor = cnx.cursor()

    

    query3 = """ SELECT image, book_name, price FROM books ORDER BY date_upload DESC ;"""



    cursor.execute(query3)
    result3=cursor.fetchall()
    print("\n\n\nresult3, ordered? \n\n",result3)

    ree=[]
    ree2=[]
    ree3=[]
    ree4=[]


    for y in result3[:8]:
        print("\n\nkinda nice i gues: \n\n",y)
        ree.append(y[0])
        ree2.append(y[1])
        ree3.append(y[2])

    print("\n\n\nall books in nice form \n\n",ree)
    

    print("\n\n\nhelloooooo2:  \n\n   ",ree2)
    print("\n\n\nprice:   \n \n ",ree3)

    cursor.close()
    cnx.close()


    
    return render_template("dashboard.html",re=zip(re,re2,re3),ree=zip(ree,ree2,ree3))





@app.route("/product_page", methods=["GET", "POST"])
def product_page():
    if request.method=="POST":
        p=""
        
        o=request.form["list"]
        #print("this is varient:",o)
        
        result = db.session.query(books).filter(books.book_name==o)
        db.session.commit()
        #print("this is the result",result)

        book_id=result[0].id

        seller_id=result[0].seller_id

        book_name=result[0].book_name
        #print("booknamenigga",book_name)

        price=result[0].price
        #print("price",price)

        image=result[0].image
        #print("image",image)

        details=result[0].details
        #print("details",details)

        author=result[0].author
        #print("author",author)

        seller = User.query.get(seller_id)
        if seller.sales>0:
            rating = round((seller.total_rating/seller.sales),2)
        else:
            rating = None

     

        
        return render_template('product_page.html',rating = rating,seller=seller,book_id=book_id, book_name=book_name,price=price,image=image,details=details,author=author)    
    
    else:print("ERROR!")


#~~~~~~~~~~~~~~~ HERE BOIIIIIII ~~~~~~~~~~~~~~~~

# Monday: oke aryan, you did the linking products to product page thing, well done, its only done on product page tho
# you are also done with the form to upload these products to the database, noice!
# whats left is: 
# 1. make those home products linked to product page as well
# 2. make the buy btn work, along with the payment portal
# 3. database to store order info and customer data
# 4. sort latest products section, and make that shit work
# 5. clean up of these about and contact pages
# 6. change some front end shit idk
# 7. if time left then, work on some functions to improve
# gn now, its literally 4:12 am, fokin monday tomorrow







@app.route("/sell_book", methods=["GET", "POST"])
@login_required
def sell_book():


    if request.method=="POST":
       book_name=request.form.get("book_name",False)
       book_price=request.form.get("book_price",False)
       book_description=request.form.get("book_description",False)
       book_author=request.form.get("book_author",False)
       book_img_link=request.form.get("book_img_link",False)

      
    
       add_book(book_name,book_price,book_img_link,book_description,book_author)


           

    
       return render_template("sell_book.html",message="Product details uploaded successfully! You may continue browsing.")

    return render_template("sell_book.html")



@app.route("/about", methods=["GET", "POST"])
def about():
    
    return render_template("about.html")





@app.route("/contact", methods=["GET", "POST"])
def contact():
    
    return render_template("contact.html")







@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    if request.method=="POST":
        book_id=request.form.get("book_id",False)
        # seller_id=request.form.get("seller_id",False)
        book_name=request.form.get("book_name",False)
        book_price=request.form.get("book_price",False)
        book_description=request.form.get("book_description",False)
        book_author=request.form.get("book_author",False)
        book_img_link=request.form.get("book_img_link",False)

       

    return render_template("checkout.html",book_id = book_id,book_name=book_name,price=book_price,image=book_img_link,details=book_description,author=book_author)





@app.route('/checkout_cart', methods = ['GET', 'POST'])
@login_required
def checkout_cart():

    return render_template('checkout_cart.html')








#Checkout for cart purchases
@app.route("/post_checkout", methods=["GET", "POST"])
@login_required
def post_checkout():
    if request.method == 'POST':
        cart_list = current_user.cart
        customer_name=request.form.get("customer_name",False)
        customer_number=request.form.get("customer_number",False)
        customer_address=request.form.get("customer_address",False)
        total_books = []
        for i in cart_list:
            if i==0:
                continue
            book = books.query.get(i)
            total_books.append(book)

        buyer_email(total_books)
        flash('An email has been sent to you with details regarding your order.', 'info')
        
        for book in total_books:
            seller_email(book)
            buy_login_id = add_buy_log(book,customer_name,customer_number,customer_address)
        #     new_buyer = buy_log()
        #     new_buyer.customer_name = customer_name
        #     new_buyer.customer_number = customer_number
        #     new_buyer.customer_address = customer_address
        #     new_buyer.book_name = book.book_name
        #     new_buyer.price = book.price
        #     new_buyer.details = book.details
        #     new_buyer.author = book.author
        #     new_buyer.date_upload = book.date_upload
        #     new_buyer.date_sold = datetime.now()
        #     db.session.add(new_buyer)
        #     books.query.filter_by(id = int(i)).delete()
            current_user.orders = buy_login_id
            db.session.commit()

        current_user.empty_cart()
        db.session.commit()



    return redirect(url_for('confirmation'))



def buyer_email(books):
    all_books = []
    for book in books:
        all_books.append(book.book_name)
    n2 = '\n\t'
    msg = Message('Your order has been placed successfully!', sender = 'noreply@demo.com', recipients = [current_user.email])
    msg.body = f'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The books you've ordered are as follows -->{n2}{n2.join(all_books)}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
    mail.send(msg)



    # def get_reset_token(self, expires_sec = 1800):
    #     s = Serializer(app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')


    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer('secret')
    #     try:
    #         user_id = s.loads(token)['user_id']
    #         #s.loads(token)['user_id'] = None
    #     except:
    #         return None
    #     return User.query.get(user_id)



def rate_seller_email(book, buy_log_id):
    s = Serializer(app.config['SECRET_KEY'])
    token = s.dumps({'user_id': buy_log_id}).decode('utf-8')



def seller_email(book):
    seller = User.query.get(book.seller_id)
    msg = Message('Book buying request', sender = 'noreply@demo.com', recipients = [seller.email])
    msg.body = f'''Your book {book.book_name} has got a new buyer.

It shall be sold to {current_user.username}.
'''
    mail.send(msg)




@app.route("/database_editor", methods=["GET", "POST"])
@login_required
def database_editor():

    if request.method=="POST":

        book_id=request.form.get("book_id",False)
        # seller_id=request.form.get("seller_id",False)
        book_name=request.form.get("book_name",False)
        book_price=request.form.get("book_price",False)
        book_description=request.form.get("book_description",False)
        book_author=request.form.get("book_author",False)
        book_img_link=request.form.get("book_img_link",False)

        customer_name=request.form.get("customer_name",False)
        customer_number=request.form.get("customer_number",False)
        customer_address=request.form.get("customer_address",False)

        print("\n\n\nbook_name\n\n",book_name)




        cnx = mysql.connector.connect(user='root', database='information')
        cursor = cnx.cursor()

        query2 = """ SELECT date_upload FROM books WHERE book_name='"""+str(book_name)+"""' """

        cursor.execute(query2)
        result=cursor.fetchall()

        print("resultyo: ",result)

        for x in result:
            print("this is x:",x[0])
            date_upload=x[0]

        cursor.close()
        cnx.close()

        book = books.query.get(book_id)

        buyer_email([book])
        seller_email(book)
        flash('An email has been sent to you with details regarding your order.', 'info')

        buy_log_id = add_buy_log(book,customer_name,customer_number,customer_address)
        current_user.orders = buy_log_id
        db.session.commit()
            
        # delete_book(book_name,book_price,book_img_link,book_description,book_author)




    return redirect(url_for('confirmation'))
    
    
    



@app.route("/confirmation", methods=["GET", "POST"])
@login_required
def confirmation():


    return render_template("confirmation.html")



@app.route("/products", methods=["GET", "POST"])
def products():

    cnx = mysql.connector.connect(user='root', database='information')
    cursor = cnx.cursor()

    
    query2 = """ SELECT image, book_name, price FROM books """


    cursor.execute(query2)
    result=cursor.fetchall()

    #print("henlo",result)


    re=[]
    re2=[]
    re3=[]


    for x in result:
        #print("BRUHHHH:   ",x)
        re.append(x[0])
        re2.append(x[1])
        re3.append(x[2])

    #print("hellooo   ",re)
    #print("helloooooo2:     ",re2)
    #print("price:     ",re3)
    cursor.close()
    cnx.close()

    
    return render_template("products.html",re=zip(re,re2,re3))



@app.route("/search")
def search():
    return render_template("search.html", title = 'Search')




@app.route("/result", methods = ['GET','POST'])
def result():
    if request.method == 'POST':
        book_title = request.form.get('title')
        author_name = request.form.get('author')
        #session = Session()
        list1 = []

        arr = books.query.all()

        for i in arr:
            if book_title.lower() in (i.book_name).lower():
                list1.append(i)
        
        if list1 == []:
            flash("Sorry, we could not find any book with that name. :(")

        return render_template("result.html", title = 'Search result', count = len(list1), book_results = list1)








@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book_details(id):
    book = books.query.get(id)
    seller = User.query.get(book.seller_id)
    if seller.sales>0:
        rating = round((seller.total_rating/seller.sales),2)
    else:
        rating = None

    return render_template('product_page.html',rating = rating,seller = seller,book_id = book.id,book_name=book.book_name,price=book.price,image=book.image,details=book.details,author=book.author)







@app.route('/empty_cart')
@login_required
def empty_cart():
    current_user.empty_cart()
    db.session.commit()

    return redirect(url_for('cart'))







@app.route('/remove_from_cart/<int:index>', methods=['GET', 'POST'])
@login_required
def remove_from_cart(index):
    cart_list = current_user.cart
    cart_list.pop(index+1)
    new_list = map(str, cart_list)

    s = '-'
    new_cart = s.join(new_list)
    current_user.reset(new_cart)

    db.session.commit()

    return redirect(url_for('cart'))









@app.route('/add_to_cart/<string:name>', methods=['GET', 'POST'])
@login_required
def add_to_cart(name):
    book = books.query.filter_by(book_name = name).first()
    cart_list = current_user.cart
    if book.id in cart_list:
        flash('The book already exists in your cart.', 'info')
    else:
        string_id = str(book.id)
        current_user.cart = string_id
        db.session.commit()
        flash('The book has been added to your cart.', 'success')

    return redirect(url_for('book_details', id = book.id))





@app.route('/cart')
@login_required
def cart():

    cart_list = current_user.cart

    all_books = books.query.all()

    list1 = []

    total_price = 0.00

    for i in cart_list:
        if i == '0':
            continue
        for j in all_books:
            if j.id == i:
                total_price += int(j.price)
                list1.append(j)
                break
    
    if list1 == []:
        flash("There's no book in your cart.")


    return render_template('cart.html', title = 'My Cart', count = len(list1), book_results = list1, total_price = total_price)





def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender = 'noreply@demo.com', recipients = [user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token = token, _external = True)}

If you did not make this request, then simply ignore this email and no changes will be made.
'''
    mail.send(msg)





@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    
    return render_template('reset_request.html', title = 'Reset Password', form = form)




@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    
    form = PasswordResetForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now Log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title = 'Reset Password', form = form)



# @app.route('/rate_seller/<token>', methods=['GET', 'POST'])
# def rate(token):

#     return render_template('rate.html', title = 'Rate Your Seller')


@app.route('/orders')
@login_required
def orders():
    orders_list = []
    list1 = current_user.orders
    
    for temp in list1:
        if temp == 0:
            continue
        order = buy_log.query.get(temp)
        orders_list.append(order)
    
    if orders_list == []:
        flash("You haven't ordered anything yet. :(")

    return render_template('orders.html', title='My Orders', orders_list = orders_list, count=len(orders_list))


@app.route('/set_rating/<int:rating>/<int:buy_log_id>', methods=['GET', 'POST'])
def set_rating(rating, buy_log_id):
    temp = buy_log.query.get(buy_log_id)
    if temp.rating>0:
        return redirect(url_for('orders'))
    temp.rating = rating
    seller = User.query.get(temp.seller_id)
    sales = seller.sales
    sales += 1
    seller.sales = sales
    total_rating = seller.total_rating
    total_rating += rating
    seller.total_rating = total_rating
    db.session.commit()
    return redirect(url_for('orders'))



if __name__ == "__main__":
    app.run(debug=True)
     

