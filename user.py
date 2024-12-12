# user.py
import hashlib
from baseObject import baseObject

class User(baseObject):
    def __init__(self):
        self.setup()
        self.tn = 'user'

    def hash_password(self, password):
        password = password + 'xyz'
        return hashlib.md5(password.encode('utf-8')).hexdigest()


    def verify_new(self, n=0):
        self.errors = []
        if self.data[n]['username'] == '':
            self.errors.append('Username cannot be blank.')
        else:
            u = User()
            u.getByField('username', self.data[n]['username'])
            if len(u.data) > 0:
                self.errors.append('Username already in use.')

        if len(self.data[n]['password']) < 3:
            self.errors.append('Password needs to be more than 3 chars.')
        elif self.data[n]['password'] != self.data[n]['confirm_password']:
            self.errors.append('Passwords do not match.')
        else:
            self.data[n]['password'] = self.hash_password(self.data[n]['password'])

        return len(self.errors) == 0

    
    def verify_update(self,n=0):
        self.errors = []

        if self.data[n]['username'] == '':
            self.errors.append('Name cannot be blank.')
        else:
            u = User()
            u.getByField('name',self.data[n]['username'])
            if len(u.data) > 0 and u.data[0][u.pk] != self.data[n][self.pk]:
                self.errors.append('Name already in use.')

        if len(self.errors) > 0:
            return False
        else:
            return True
        
    def register_user(self, username, password, confirm_password):
        self.createBlank()
        self.data[0]['username'] = username
        self.data[0]['password'] = password
        self.data[0]['confirm_password'] = confirm_password

        if self.verify_new():
            self.insert()
            return True
        else:
            print(f"Registration errors: {self.errors}")
            return False

    def tryLogin(self,username, password):
        pwd = self.hash_password(password)
        sql = f"Select * from `{self.tn}` where `username` = %s AND `password` = %s;" 
        print(sql,(username, pwd))
        print(sql,(username,password))
        self.cur.execute(sql,(username, pwd))
        self.data = []
        for row in self.cur:
            self.data.append(row)
        if len(self.data) == 1:
            return True
        else:
            return False
    
