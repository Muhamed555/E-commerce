from flask import render_template, url_for, flash, redirect, request, session
from group import app, db, bcrypt
from group.forms import RegistrationForm, LoginForm
from group.models import User, Products, Cart
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func, update
from product_recommender import *


def getLoginDetails():
    if current_user.is_authenticated:
        noOfItems = Cart.query.filter_by(buyer=current_user).count()
    else:
        noOfItems = 0
    return noOfItems


@app.route("/")
@app.route("/home")
def main():
    noOfItems = getLoginDetails()
    # display items in cart
    return render_template('home.html')



@app.route("/register", methods=['GET', 'POST'])
def register(hashed_password=None):
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(str(form.password.data)).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, str(form.password.data)):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for('main'))



        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route('/profile')
@login_required
def profile():
    noOfItems = getLoginDetails()
    firstname = current_user.firstname
    # display items in cart
    cartOfAll = Products.query.join(Cart).add_columns(Cart.quantity, Products.Price, Products.Name,
                                                      Products.body_loc, Products.id, Products.Image,
                                                      Products.Category).filter_by(
        buyer=current_user).all()
    subtotal = 0
    for num in cartOfAll:
        subtotal += num.quantity

    return render_template('profile.html', cartOfAll=cartOfAll, noOfItems=noOfItems, firstname = firstname)



@app.route("/products/", methods=['GET', 'POST'])
@app.route("/products/<name>")
def select_products(name=None):
    noOfItems = getLoginDetails()
    products = Products.query.all()
    if name:
        for i in products:
            if i.Name == name:
                product_info = Products.query.get(i.id)
                recommended_index_products = recommender(i.id - 1)
                recommended_products = []
                for id_o in recommended_index_products:
                    p = Products.query.get(id_o + 1)
                    recommended_products.append(p)

                return render_template("product.html", product_info=product_info,
                                       recommended_products=recommended_products)

    return render_template('products.html', products=products, noOfItems=noOfItems)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/addToCart/<int:product_id>")
@login_required
def addToCart(product_id):
    # check if product is already in cart
    row = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    if row:
        # if in cart update quantity : +1
        row.quantity += 1
        db.session.commit()
        flash('This item is already in your cart, 1 quantity added!', 'success')

        # if not, add item to cart
    else:
        user = User.query.get(current_user.id)
        user.add_to_cart(product_id)
    return redirect(url_for('select_products'))



## Handle unkown pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
