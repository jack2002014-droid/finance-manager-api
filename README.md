markdown
# Finance Manager API

**Finance Manager API** is a REST API for personal finance management. The project allows you to create users, add incomes and expenses, view balance and transaction history.

## Technologies

- Python 3.10
- Flask
- MySQL
- Postman

## Features

- User creation
- Add incomes and expenses
- Calculate balance
- View transaction history
- REST API with JSON responses

## Installation and Setup

### 1. Clone repository
```bash
git clone https://github.com/ogromish/finance-manager-api.git
cd finance-manager-api
2. Install dependencies
bash
pip install flask mysql-connector-python
3. Database setup
sql
CREATE DATABASE finance_db;
USE finance_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
4. Configure connection
In db.py file specify your MySQL password:

python
password = 'your_password'  # leave empty if no password
5. Run server
bash
python app.py
Server will start at http://127.0.0.1:5000

API Endpoints
Method	URL	Description
POST	/user	Create user
POST	/transaction	Add transaction
GET	/balance/<user_id>	Get balance
GET	/transactions/<user_id>	Transaction history
Request Examples
Create user
bash
POST /user
{
    "name": "John Doe",
    "email": "john@mail.ru"
}
Add income
bash
POST /transaction
{
    "user_id": 1,
    "amount": 50000,
    "type": "income",
    "category": "salary",
    "description": "Monthly salary"
}
Add expense
bash
POST /transaction
{
    "user_id": 1,
    "amount": 3500,
    "type": "expense",
    "category": "groceries",
    "description": "Supermarket"
}
Get balance
bash
GET /balance/1
Get history
bash
GET /transactions/1?limit=5
Project Structure
text
finance-manager-api/
│
├── app.py                 # API server
├── db.py                  # Database connection
├── finance_manager.py     # Business logic
├── requirements.txt       # Dependencies
└── README.md              # Documentation
Dependencies
Create requirements.txt file:

text
flask==2.3.3
mysql-connector-python==8.1.0
Install:

bash
pip install -r requirements.txt
Author
ogromish

GitHub: @ogromish

