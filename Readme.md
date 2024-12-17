## Book Club Management Application

#### Group members:
##### 1.Kusala Nagamani Reddy

#### Narrative or Description:
###### The Book Club Management Application is a Flask and myPHPAdmin web-based platform designed to streamline the operations of an online book club. The application serves two primary user roles: Users and Admin.

#### Users can: 
###### 1.Able to Register and login the page
###### 2.Browse  books in Book section.
###### 3.Add books to their cart and place orders.
###### 4.View their order history.
###### 5.Able to Logout from the session

#### Admin can:
###### 1.Add, update, and delete books from the catalog.
###### 2.Perform data-driven analytics via the Admin Dashboard.

##### The Admin Dashboard provides key insights such as total sales, top-selling books, and active user metrics, along with graphical visualizations for better decision-making.

 
#### Relational Schema: 

![Relational Schema](relational.png)

#### Home Page
![Home](https://github.com/user-attachments/assets/8bca5bda-b594-424f-853a-13621e35e4b5)

#### Register Page
![Register](https://github.com/user-attachments/assets/38ae63f0-f558-48ef-b0f0-ae68eb474b36)

#### Login Page
![Login](https://github.com/user-attachments/assets/591f6380-1f9b-4d46-8f67-318c79ca0313)

#### Admin Login Page
![Admin](https://github.com/user-attachments/assets/d85fff9f-c13e-41dc-99b8-d559b54703a3)

#### Admin Home Page
![Admin Home page](https://github.com/user-attachments/assets/fab85f93-7865-4e5c-9089-7bc8aa35faf0)

#### Admin Manage Books
![Manage Books](https://github.com/user-attachments/assets/acfd5c67-0abb-414b-979a-94a282075b98)

#### ADD Book
![Add_book](https://github.com/user-attachments/assets/a7655451-d2a5-4dcb-b912-b8d7431003ad)

#### Update Book
![update book](https://github.com/user-attachments/assets/acdb5847-9d54-4310-aada-00092b5bdfc8)

#### User Main Page
![Main Page](https://github.com/user-attachments/assets/2287459a-70a3-4e41-ba56-9668da85abc0)

#### User Navigate to Books
![Books](https://github.com/user-attachments/assets/23d86049-7505-4d51-b0b0-3d7cb9623166)

#### Select the book for add to cart
![Add to cart](https://github.com/user-attachments/assets/26c2d6e6-d5ac-48c4-9531-4d0d5ed59d35)

#### Book added to Cart
![Books added to cart](https://github.com/user-attachments/assets/158fffc9-055e-40f6-a1da-2660fa8c8ede)

#### Proceed to checkout and Billing
![checkout](https://github.com/user-attachments/assets/088d3219-3b9b-4e4c-b421-d1096962acd6)

#### Order Placed
![orderplaced](https://github.com/user-attachments/assets/bcbf2d61-d960-4de8-8d2f-f325d1dceb99)

#### Order details
![order details](https://github.com/user-attachments/assets/2e6086b2-0639-4eea-aaf1-0428eff7244b)

#### Log out
![Loggout](https://github.com/user-attachments/assets/4a79d1af-fa99-4909-978b-1577e23ee0d2)

#### Dashboard
![Dashboard](https://github.com/user-attachments/assets/cd512987-49ea-419a-ba77-6df65589930a)

#### Analytical Queries in Admin Dashboard:

#### 1.Total sales:
###### Select SUM(b.price * c.quantity) AS total_sales FROM cart c 
JOIN book b ON c.book_id = b.id;

#### 2.Top Selling Books:
###### SELECT b.title, SUM(c.quantity) AS total_quantity FROM cart c 
JOIN book b ON c.book_id = b.id

GROUP BY b.id

ORDER BY total_quantity DESC

LIMIT 5;

#### 3.Active Users
###### SELECT u.username, COUNT(DISTINCT o.id) AS order_count

FROM user u

JOIN orders o ON u.id = o.user_id

GROUP BY u.id

ORDER BY order_count DESC

LIMIT 10;




