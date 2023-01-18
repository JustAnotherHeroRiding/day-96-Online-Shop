from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import dotenv
import os
from forms import LoginForm, RegisterForm
import stripe
dotenv.load_dotenv()



# Build command tailwind
# npx tailwindcss -i src/input.css -o src/static/dist/output.css --watch

tax = 0
shipping = 0

os.getenv("APIKEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("APIKEY")

login_manager = LoginManager()
login_manager.init_app(app)

from jinja2 import Environment, select_autoescape
from decimal import Decimal

def round_filter(value, precision):
    return Decimal(value).quantize(Decimal(f'0.{str(0)*precision}'))


env = Environment(autoescape=select_autoescape(['html', 'xml']))
env.filters['round'] = round_filter


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersandcart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


stripe_keys = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
    "endpoint_secret": os.getenv("STRIPE_ENDPOINT_SECRET"), 
}
stripe.api_key = stripe_keys["secret_key"]

product_data = [
    {"name": "Fender Stratocaster", "price": "799", "img_url": "https://www.example.com/stratocaster.jpg",
        "description": "The Fender Stratocaster is a classic electric guitar, known for its sleek design and versatile sound.", "category": "Electric Guitars", "subcategory": "Stratocaster"},
    {"name": "Gibson Les Paul Standard", "price": "1499", "img_url": "https://www.example.com/lespaul.jpg",
        "description": "The Gibson Les Paul Standard is a solid body electric guitar known for its rich, warm tone and sustain.", "category": "Electric Guitars", "subcategory": "Les Paul"},
    {"name": "Taylor 214ce", "price": "1149", "img_url": "https://www.example.com/214ce.jpg",
        "description": "The Taylor 214ce is a grand auditorium size acoustic guitar, featuring a solid Sitka spruce top and laminate back and sides.", "category": "Acoustic Guitars", "subcategory": "Grand Auditorium"},
    {"name": "Martin D-28", "price": "3199", "img_url": "https://www.example.com/d28.jpg",
        "description": "The Martin D-28 is a classic dreadnought size acoustic guitar, featuring a solid Sitka spruce top and rosewood back and sides.", "category": "Acoustic Guitars", "subcategory": "Dreadnought"},
    {"name": "Yamaha APX600", "price": "499", "img_url": "https://www.example.com/apx600.jpg",
        "description": "The Yamaha APX600 is a thinline cutaway acoustic-electric guitar, featuring a solid spruce top and nato back and sides.", "category": "Acoustic Guitars", "subcategory": "Thinline Cutaway"},
    {"name": "Epiphone SG Special", "price": "199", "img_url": "https://www.example.com/sg.jpg",
        "description": "The Epiphone SG Special is a solid body electric guitar, featuring a mahogany body and neck, and a rosewood fingerboard.", "category": "Electric Guitars", "subcategory": "SG"},
    {"name": "Jackson JS32 Dinky", "price": "349", "img_url": "https://www.example.com/js32.jpg",
        "description": "The Jackson JS32 Dinky is a solid body electric guitar, featuring a poplar body, maple neck and rosewood fingerboard.", "category": "Electric Guitars", "subcategory": "Dinky"},
    {"name": "Ibanez RG450", "price": "449", "img_url": "https://www.example.com/rg450.jpg", "description": "The Ibanez RG450 is a solid body electric guitar, featuring a basswood body, maple neck and rosewood fingerboard.", "category": "Electric Guitars", "subcategory": "RG"}]


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    tasks = db.relationship('CartItem', backref='owner')

    def __repr__(self):
        return f'User{self.first_name}{self.email}'


class ShopItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.String(255))
    img_url = db.Column(db.String)
    description = db.Column(db.String)
    category = db.Column(db.String)
    subcategory = db.Column(db.String)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255))
    price = db.Column(db.String(255))
    quantity = db.Column(db.Integer())
    img_url = db.Column(db.String)
    shop_item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'))
    cart_owner = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


with app.app_context():
    db.create_all()
# for item in product_data:
    # product = ShopItem(name=item['name'], price=item['price'], img_url=item['img_url'], description=item['description'], category=item['category'], subcategory=item['subcategory'])
    # db.session.add(product)
    # db.session.commit()


@app.route("/", methods=["GET", "POST"])
def home_page():
    global tax,shipping
    loginform = LoginForm()
    registerform = RegisterForm()
    products = ShopItem.query.all()
    cart = CartItem.query.all()
    total = 0
    tax = 0
    shipping = 0
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(cart_owner=current_user.id).all()
        for item in cart_items:
            total += int(item.price)
            tax += 0.18*int(item.price)
            shipping += 8
    if registerform.validate_on_submit():
        user = User(first_name=registerform.first_name.data,
                    last_name=registerform.last_name.data,
                    email=registerform.email.data,
                    password=generate_password_hash(registerform.password.data)
                    )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home_page'))
    elif loginform.validate_on_submit():
        user = User.query.filter_by(email=loginform.email.data).first()
        if user and check_password_hash(user.password, loginform.password.data):
            login_user(user)
            return redirect(url_for('home_page'))
        flash("Invalid details")
    return render_template("index.html", tax=tax, shipping=shipping,loginform=loginform,total = total,cart=cart, registerform=registerform, products=products)

#For stripe checkout
@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

@app.route("/success",methods = ["GET","POST"])
def success():
    global tax,shipping
    loginform = LoginForm()
    registerform = RegisterForm()
    products = ShopItem.query.all()
    cart = CartItem.query.all()
    total = 0
    tax = 0
    shipping = 0
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(cart_owner=current_user.id).all()
        for item in cart_items:
            db.session.delete(item)
        db.session.commit()
    
    if registerform.validate_on_submit():
        user = User(first_name=registerform.first_name.data,
                    last_name=registerform.last_name.data,
                    email=registerform.email.data,
                    password=generate_password_hash(registerform.password.data)
                    )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('success'))
    elif loginform.validate_on_submit():
        user = User.query.filter_by(email=loginform.email.data).first()
        if user and check_password_hash(user.password, loginform.password.data):
            login_user(user)
            return redirect(url_for('success'))
        flash("Invalid details")

    return render_template("success.html", tax=tax,shipping=shipping, total = total ,loginform = loginform, registerform=registerform, products=products,card=cart)


@app.route("/cancelled",methods = ["GET","POST"])
def cancelled():
    global tax,shipping
    loginform = LoginForm()
    registerform = RegisterForm()
    products = ShopItem.query.all()
    cart = CartItem.query.all()
    total = 0
    tax = 0
    shipping = 0
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(cart_owner=current_user.id).all()
        for item in cart_items:
            total += int(item.price)
            tax += 0.18*int(item.price)
            shipping += 8
            
    if registerform.validate_on_submit():
        user = User(first_name=registerform.first_name.data,
                    last_name=registerform.last_name.data,
                    email=registerform.email.data,
                    password=generate_password_hash(registerform.password.data)
                    )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('cancelled'))
    elif loginform.validate_on_submit():
        user = User.query.filter_by(email=loginform.email.data).first()
        if user and check_password_hash(user.password, loginform.password.data):
            login_user(user)
            return redirect(url_for('cancelled'))
        flash("Invalid details")
    return render_template("cancelled.html", tax=tax,shipping=shipping ,total = total ,loginform = loginform, registerform=registerform, products=products,card=cart)

""" @app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://127.0.0.1:5000/"
    stripe.api_key = stripe_keys["secret_key"]

    #dictionary for all products in the cart
    products = {}
    cart_items = CartItem.query.filter_by(cart_owner=current_user.id).all()
    for item in cart_items:
        product = stripe.Product.create(
            #before i just had a hardcoded fender strat
        name=item.name
        )
        #under the key name we add the product
        products['name'] = product
        products['sqlprice'] = item.price

    # Create a price in the Stripe Dashboard and associate it with the product
    for product,sqlprice in products['name'],products["sqlprice"]:
        #Here again i had hardcoded values for the price and the one product we created above
        #now i am trying to create products for everything in the cart
        price = stripe.Price.create(
            unit_amount=f"{sqlprice}00",
            currency='usd',
            product=product.id
        )
        #3rd key in our dictionary
        products['price'] = price

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 403
     """
    
    
@app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://127.0.0.1:5000/"
    stripe.api_key = stripe_keys["secret_key"]

    #dictionary for all products in the cart
    products = {}
    cart_items = CartItem.query.filter_by(cart_owner=current_user.id).all()
    for item in cart_items:
        product = stripe.Product.create(
            name=item.item_name
        )
        #under the key name we add the product
        products[item.item_name] = {'product': product}
        products[item.item_name]['sqlprice'] = item.price

    # Create a price in the Stripe Dashboard and associate it with the product
    for product_name,product_data in products.items():
        price = stripe.Price.create(
            unit_amount=f"{product_data['sqlprice']}00",
            currency='usd',
            product=product_data['product'].id
        )
        #3rd key in our dictionary
        products[product_name]['price'] = price

    try:
        line_items = []
        for item in cart_items:
            line_items.append({
                "price": products[item.item_name]['price'].id,
                "quantity": item.quantity
            })
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 403


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")
        # TODO: run some custom code here

    return "Success", 200


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    global tax,shipping
    total = 0
    tax = 0
    shipping = 0
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(cart_owner=current_user.id).all()
        for item in cart_items:
            total += int(item.price)
            tax += 0.18*int(item.price)
            shipping += 8
    loginform = LoginForm()
    registerform = RegisterForm()
    product = ShopItem.query.filter_by(id=product_id).first()
    cart = CartItem.query.all()
    allproducts = ShopItem.query.all()
    if registerform.validate_on_submit():
        user = User(first_name=registerform.first_name.data,
                    last_name=registerform.last_name.data,
                    email=registerform.email.data,
                    password=generate_password_hash(registerform.password.data)
                    )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('product',product_id=product_id))
    elif loginform.validate_on_submit():
        user = User.query.filter_by(email=loginform.email.data).first()
        if user and check_password_hash(user.password, loginform.password.data):
            login_user(user)
            return redirect(url_for('product', product_id=product_id))
        flash("Invalid details")
    return render_template("product.html", tax=tax,shipping=shipping,product=product, total=total,products=allproducts, loginform=loginform, registerform=registerform, cart=cart)


@app.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    # get the product details from the database using the product_id
    product = ShopItem.query.filter_by(id=product_id).first()
    item_name = product.name
    price = product.price
    quantity = 1  # set the quantity to 1 as default
    shop_item_id = product_id
    cart_item = CartItem(item_name=item_name,
                         price=price,
                         quantity=quantity,
                         img_url = product.img_url,
                         shop_item_id=shop_item_id,
                         cart_owner=current_user.id)

    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('product', product_id=product_id))


@app.route('/cart/item/<int:item_id>', methods=['DELETE', 'POST'])
def remove_item(item_id):
    item = CartItem.query.filter_by(id=item_id).first()
    db.session.delete(item)
    db.session.commit()
    return make_response('', 204)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged yourself out.')
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run(debug=True)
