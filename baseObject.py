import pymysql
import yaml
from pathlib import Path



class baseObject:
    def setup(self):
        config = yaml.safe_load(Path("config.yml").read_text())
        self.config = config
        self.tn = self.config['tables'][type(self).__name__]
        self.conn = None
        self.cur = None
        self.pk = None
        self.fields = []
        self.errors = []
        self.data = []
        self.establishConnection()
        self.getFields()
    def establishConnection(self):
        config = self.config
        #print(config)
        self.conn = pymysql.connect(host=config['db']['host'], port=config['db']['port'], user=config['db']['user'],
                       passwd=config['db']['passwd'], db=config['db']['db'], autocommit=True)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor) 
    def set(self,d):
        self.data.append(d)
    def getFields(self):
        sql = f'''DESCRIBE `{self.tn}`;'''
        self.cur.execute(sql)
        for row in self.cur:
            if row['Extra'] == 'auto_increment':
                self.pk  = row['Field']
            else:
                self.fields.append(row['Field'])
    def insert(self,n=0):
        count = 0
        vals = []
        sql = f"INSERT INTO `{self.tn}` ("
        for field in self.fields:
            sql += f"`{field}`,"
            vals.append(self.data[n][field])
            count +=1
        sql = sql[0:-1] + ') VALUES ('
        tokens = ("%s," * count)[0:-1]
        sql += tokens + ');'
        #print(sql,vals)
        self.cur.execute(sql,vals)
        self.data[n][self.pk] = self.cur.lastrowid
    def createBlank(self):
        d = {}
        for field in self.fields:
            d[field] = ''
        self.set(d)
    def getById(self,id):
        sql = f"Select * from `{self.tn}` where `{self.pk}` = %s" 
        self.cur.execute(sql,(id))
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def getAll(self):
        sql = f"Select * from `{self.tn}`" 
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def truncate(self):
        sql = f"TRUNCATE TABLE `{self.tn}`" 
        self.cur.execute(sql)
    def getByField(self,field,val):
        sql = f"Select * from `{self.tn}` where `{field}` = %s" 
        #print(sql,val)
        self.cur.execute(sql,(val))
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def update(self,n=0):
        vals=[]
        fvs=''
        for field in self.fields:
            if field in self.data[n].keys():
                fvs += f"`{field}`=%s,"
                vals.append(self.data[n][field])
        fvs=fvs[:-1]
        sql=f"UPDATE `{self.tn}` SET {fvs} WHERE `{self.pk}` = %s"
        vals.append(self.data[n][self.pk])
        #print(sql,vals)
        self.cur.execute(sql,vals)
    def deleteById(self,id):
        sql = f"Delete from `{self.tn}` where `{self.pk}` = %s" 
        self.cur.execute(sql,(id))

class Book(baseObject):
    def __init__(self):
        super().__init__()
        self.setup()

    def getBooks(self):
        self.getAll()
        return self.data

    def addBook(self, book_data):
        self.createBlank()
        for key, value in book_data.items():
            self.data[0][key] = value
        self.insert()
        
    def delete(self, book_id):
        try:
            sql = f"DELETE FROM {self.tn} WHERE id = %s"
            self.cur.execute(sql, (book_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting book: {e}")
    
    def getBooks(self):
      self.getAll()
      return self.data
    
class Cart(baseObject):
    def __init__(self):
        super().__init__()
        self.setup()

    def clear_cart(self, user_id=None, session_id=None):
        """
        Clear cart items for the specified user or session.
        If `user_id` is provided, it will clear items for that user.
        Otherwise, it will clear items for the session.
        """
        try:
            if user_id:
                sql = "DELETE FROM cart WHERE user_id = %s"
                self.cur.execute(sql, (user_id,))
            elif session_id:
                sql = "DELETE FROM cart WHERE session_id = %s"
                self.cur.execute(sql, (session_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error clearing cart: {e}")
            self.conn.rollback()


    def add_to_cart(self, session_id,user_id, book_id, quantity):
        """
        Adds a book to the cart or updates the quantity if the book already exists.
        """
        try:
            sql = """
            INSERT INTO cart (session_id, user_id,book_id, quantity,created_at,updated_at)
            VALUES (%s, %s, %s,%s,NOW(),NOW())
            ON DUPLICATE KEY UPDATE
            quantity = quantity + VALUES(quantity),updated_at=NOW();
            """
            self.cur.execute(sql, (session_id,user_id, book_id, quantity))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding to cart: {e}")

    def get_cart_items(self, session_id,user_id=None):
        try:
           if user_id:
            sql = """
            SELECT c.id,c.book_id, c.quantity, b.title, b.price,b.image_path,(b.price * c.quantity) AS total
            FROM cart c
            JOIN book b ON c.book_id = b.id
            WHERE c.user_id = %s;
            """
            self.cur.execute(sql,(user_id,))
           else:
            sql=""" SELECT c.id,c.book_id, c.quantity, b.title, b.price,b.image_path,(b.price * c.quantity) AS total
            FROM cart c
            JOIN book b ON c.book_id = b.id
            WHERE c.session_id= %s; """
            self.cur.execute(sql, (session_id,))
           cart_items = self.cur.fetchall()
           return cart_items if cart_items else []
        except Exception as e:
            print(f"Error retrieving cart items: {e}")
            return []
        
    def remove_item(self, cart_id):
        """
        Removes an item from the cart by its cart ID.
        """
        try:
            sql = "DELETE FROM cart WHERE id = %s"
            self.cur.execute(sql, (cart_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing item from cart: {e}")
    
    def migrate_cart(self, session_id,user_id):
        try:
            sql = "UPDATE cart SET user_id=%s WHERE session_id=%s AND user_id IS NULL"
            self.cur.execute(sql, (user_id,session_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error Migrationg cart items: {e}")

class Order(baseObject):
    def __init__(self):
        super().__init__()
        self.setup()

    def place_order(self, user_id, card_number, card_name, card_cvv, card_expiry,
                    street_address, city, state, zip_code):
        try:
            sql = """
            INSERT INTO orders (user_id, card_number, card_name, card_cvv, card_expiry,
                                street_address, city, state, zip_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cur.execute(sql, (user_id, card_number, card_name, card_cvv, card_expiry,
                                   street_address, city, state, zip_code))
            self.conn.commit()
            return self.cur.lastrowid  # Return the ID of the inserted order
        except Exception as e:
            print(f"Error placing order: {e}")
            self.conn.rollback()
            return None
    def get_user_orders(self, user_id):
        try:
            sql = """
            SELECT id, street_address, city, state, zip_code, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
            """
            self.cur.execute(sql, (user_id,))
            return self.cur.fetchall()
        except Exception as e:
            print(f"Error retrieving user orders: {e}")
            return []

    def get_total_sales(self):
        query = """
        SELECT SUM(b.price * c.quantity) AS total_sales
        FROM cart c
        JOIN book b ON c.book_id = b.id;
        """
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result['total_sales'] if result else 0

    def get_top_selling_books(self):
        query = """
        SELECT b.title, SUM(c.quantity) AS total_quantity
        FROM cart c
        JOIN book b ON c.book_id = b.id
        GROUP BY b.id
        ORDER BY total_quantity DESC
        LIMIT 5;
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_active_users(self):
        query = """
        SELECT u.username, COUNT(DISTINCT o.id) AS order_count
        FROM user u
        JOIN orders o ON u.id = o.user_id
        GROUP BY u.id
        ORDER BY order_count DESC
        LIMIT 10;
        """
        self.cur.execute(query)
        return self.cur.fetchall()





    

