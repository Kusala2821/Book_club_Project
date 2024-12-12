from flask import Flask, render_template, request, session, redirect, make_response,url_for,flash
from flask_session import Session
from datetime import timedelta
import time
import config
import datetime
from user import User
from baseObject import Book
from baseObject import Cart
from baseObject import Order
from decimal import Decimal
import pymysql



app = Flask(__name__,static_url_path='')
app.config.from_object(config)


app.config['SECRET_KEY'] = 'IA637project'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
sess = Session()
sess.init_app(app)

@app.route('/')  #route name
def home(): #view function
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        u = User()
        if u.register_user(username=username, password=password, confirm_password=confirm_password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', title='Register', errors=u.errors)

    return render_template('register.html', title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form.get('username') is not None and request.form.get('password') is not None:
        u = User()
        if u.tryLogin(request.form.get('username'), request.form.get('password')):
            print("Login successful")
            user_data = u.data[0]  # Assuming the data contains id and username
            session['user'] = {"id": user_data['id'], "username": user_data['username']}
            session['role'] = u.data[0].get('role', 'User')  # Store the role in the session
            session['active'] = time.time()
            session_id = session.sid
            user_id = user_data['id']
            cart = Cart()
            cart.migrate_cart(session_id, user_id)
            if session['role'] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('main.html', title='eBook Store - Main')
        else:
            print("Login failed: Incorrect username or password")
            return render_template('login.html', title='Sign In', msg='Incorrect username or password.')
    else:
        if 'msg' not in session.keys() or session['msg'] is None:
            m = 'Type your email and password to continue.'
        else:
            m = session['msg']
            session['msg'] = None
        return render_template('login.html', title='Sign In', msg=m)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        u = User()
        if u.tryLogin(request.form.get('username'), request.form.get('password')):
            if len(u.data) > 0:
                user_data = u.data[0] 
                if user_data.get('role') == 'Admin':
                    session['user'] = {"id": user_data['id'], "username": user_data['username']}
                #if u.data[0].get('role') == 'Admin':
                    #session['user'] = username
                    session['role'] = 'Admin'
                    session['active'] = time.time()
                    return redirect('/admin_dashboard') 
                else:
                    return render_template('admin.html', msg='Access restricted to Admin users only.')
            else:
                return render_template('admin.html', msg='Incorrect admin username or password.')
    
    return render_template('admin.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' in session and session.get('role') == 'Admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect('/admin_login')
@app.route('/dashboard')
def dashboard():
    if 'user' in session and session.get('role') == 'Admin':
        order = Order()
        total_sales = order.get_total_sales()
        top_selling_books = order.get_top_selling_books()
        active_users = order.get_active_users()
        
        return render_template(
            'dashboard.html',
            total_sales=total_sales,
            top_selling_books=top_selling_books,
            active_users=active_users
        )
    else:
        return redirect('/admin_dashboard')


@app.route('/managebooks', methods=['GET', 'POST'])
def manage_books():
    book_obj = Book()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            book_data = {
                'isbn': request.form['isbn'],
                'title': request.form['title'],
                'image_url': request.form['image_url'],
                'author': request.form['author'],
                'description': request.form['description'],
                'quantity': request.form['quantity'],
                'price': request.form['price'],
                'genre': request.form['genre'],
            }
            book_obj.addBook(book_data)

        elif action == 'update':
            book_id = request.form['book_id']
            updated_data = {
                'isbn': request.form['isbn'],
                'title': request.form['title'],
                'image_url': request.form['image_url'],
                'author': request.form['author'],
                'description': request.form['description'],
                'quantity': request.form['quantity'],
                'price': request.form['price'],
                'genre': request.form['genre'],
            }
            book_obj.updateBook(book_id, updated_data)

        elif action == 'delete':
            book_id = request.form['book_id']
            book_obj.deleteBook(book_id)

    books = book_obj.getBooks()
    return render_template('managebooks.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_data = {
            'isbn': request.form['isbn'],
            'title': request.form['title'],
            'image_path': request.form['image_path'],
            'author': request.form['author'],
            'description': request.form['description'],
            'quantity': request.form['quantity'],
            'price': request.form['price'],
            'genre': request.form['genre'],
        }
        book_obj = Book()
        try:
            book_obj.addBook(book_data)
            flash('Book added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding book: {e}', 'danger')

    return render_template('addbook.html')  # Stay on the same page


@app.route('/updatebook/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    book_obj = Book()

    if request.method == 'GET':
        # Fetch the book details
        book_obj.getById(book_id)
        if not book_obj.data:
            flash("Book not found.", "danger")
            return redirect(url_for('manage_books'))

        book = book_obj.data[0]
        return render_template('updatebook.html', book=book)

    if request.method == 'POST':
        # Get updated details from the form
        updated_data = {
            'isbn': request.form['isbn'],
            'title': request.form['title'],
            'author': request.form['author'],
            'description': request.form['description'],
            'quantity': request.form['quantity'],
            'price': request.form['price'],
            'genre': request.form['genre'],
        }

        try:
            # Update book details
            book_obj.getById(book_id)
            if not book_obj.data:
                flash("Book not found.", "danger")
                return render_template('updatebook.html', book={})

            for key, value in updated_data.items():
                book_obj.data[0][key] = value
            book_obj.update(0)  # Update the record

            # Flash success message
            flash("Book updated successfully!", "success")
        except Exception as e:
            print(f"Error updating book: {e}")
            flash("Failed to update book. Please try again.", "danger")

        book = book_obj.data[0]
        return render_template('updatebook.html', book=book)


@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book()
    try:
        book.delete(id)
        flash('Book deleted successfully. <a href="' + url_for('manage_books') + '">Manage Books</a>', 'info')
    except Exception as e:
        flash(f"Error deleting book: {e}", 'danger')
    return redirect(url_for('manage_books'))

@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')

@app.route('/books',methods=['GET', 'POST'])
def books():
    book_obj = Book()  # Create an instance of the Book class
    books = book_obj.getBooks()  # Fetch all books from the database
    return render_template('book.html', books=books)

#User Logout
@app.route('/Logout', methods=['GET', 'POST'])
def logout():
    if session.get('user') is not None:
        del session['user']
        del session['active']
        session.clear()
    return redirect(url_for('login', Logout='success'))  

#Admin logout
@app.route('/logout', methods=['GET', 'POST'])
def admin_logout():
    if session.get('user') is not None and session.get('role') == 'Admin':
        del session['user']
        del session['active']
        del session['role']
    return redirect(url_for('admin_login', logout='success')) 
 

@app.route('/book/<int:id>', methods=['GET'])
def book_details(id):
    book_obj = Book()
    book_obj.getById(id)
    if book_obj.data:
        book = book_obj.data[0]  # Get the first book record
        return render_template('book_details.html', book=book)
    else:
        return "Book not found", 404
    
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    session_id = session.sid  # Flask's session ID
    book_id = request.form['book_id']  # Book ID from the form
    quantity = int(request.form['quantity'])  # Quantity from the form

    user = session.get('user')  # Retrieve user information from the session
    user_id = user['id'] if user else None  # Use the user ID if logged in, else None

    book = Book()
    book.getById(book_id)
    if not book.data:
        return "Book not found", 404

    # Add or update the item in the cart
    cart = Cart()
    cart.add_to_cart(session_id, user_id, book_id, quantity)  # Pass user_id to the cart

    return redirect('/cart')

@app.route('/cart')
def cart():
    session_id = session.sid
    user = session.get('user')
    user_id = user['id'] if user else None

    # Fetch cart items
    cart = Cart()
    cart_items = cart.get_cart_items(session_id, user_id) or []  # Ensure cart_items is always a list

    # Calculate totals
    original_price = sum(item['price'] * item['quantity'] for item in cart_items)
    savings = original_price - sum(item['total'] for item in cart_items)
    total_price = sum(item['total'] for item in cart_items)
    shipping_fee = Decimal(0) if total_price > 50 else Decimal(5)
    tax = round(total_price * Decimal(0.08), 2)

    return render_template(
        'cart.html',
        cart_items=cart_items,
        original_price=float(original_price),
        savings=float(savings),
        shipping_fee=float(shipping_fee),
        tax=float(tax),
        total_price=float(total_price + tax + shipping_fee),
        username=user['username'] if user else "Guest"
    )

@app.route('/remove_item/<int:cart_id>', methods=['POST'])
def remove_item(cart_id):
    cart = Cart()
    cart.remove_item(cart_id)  
    return redirect('/cart')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = session.get('user')
    if not user:
        return redirect('/login')  # Redirect to login if not logged in

    # Fetch cart items and calculate summary
    cart = Cart()
    cart_items = cart.get_cart_items(session_id=None, user_id=user['id'])
    if not cart_items:
        return redirect('/cart')  # Redirect back to cart if empty

    # Calculate totals
    items_total = sum(Decimal(item['price']) * Decimal(item['quantity']) for item in cart_items)
    shipping_fee = Decimal('5.00') if items_total < Decimal('50.00') else Decimal('0.00')
    tax = round(items_total * Decimal('0.08'), 2)  # Use Decimal for tax calculation
    total_price = items_total + shipping_fee + tax

    if request.method == 'POST':
        # Get form details
        card_number = request.form.get('card_number')
        card_name = request.form.get('card_name')
        card_cvv = request.form.get('card_cvv')
        card_expiry = request.form.get('card_expiry')
        street_address = request.form.get('street_address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')

        # Place order
        order = Order()
        order_id = order.place_order(
            user_id=user['id'], card_number=card_number, card_name=card_name, 
            card_cvv=card_cvv, card_expiry=card_expiry, 
            street_address=street_address, city=city, state=state, 
            zip_code=zip_code
        )

        if order_id:
            cart.clear_cart(user_id=user['id'])  # Clear cart after order
            return redirect('/order_placed')
        else:
            return "Error placing order", 500

    return render_template(
        'checkout.html',
        username=user['username'],
        items_total=items_total,
        shipping_fee=shipping_fee,
        tax=tax,
        total_price=total_price
    )

@app.route('/order_placed', methods=['GET'])
def order_placed():
    return render_template('order_placed.html')

@app.route('/orders')
def orders():
    user = session.get('user')
    if not user:
        return redirect('/login')  # Redirect to login if not logged in

    order = Order()
    user_orders = order.get_user_orders(user_id=user['id'])

    return render_template(
        'orders.html',
        username=user['username'],
        orders=user_orders
    )




if __name__ == '__main__':
    app.run(debug=True)



