from flask import Flask, request, jsonify
from db import get_connection
import mysql.connector

app = Flask(__name__)


# Функции из finance_manager.py (немного измененные для API)
def add_user_api(name, email):
    """Добавляет нового пользователя"""
    conn = get_connection()
    if not conn:
        return None, "Ошибка подключения к БД"

    cursor = conn.cursor()

    try:
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        values = (name, email)

        cursor.execute(query, values)
        conn.commit()

        user_id = cursor.lastrowid
        return user_id, None  # Возвращаем ID и отсутствие ошибки

    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry
            return None, "Email уже существует"
        return None, str(err)
    finally:
        cursor.close()
        conn.close()


def add_transaction_api(user_id, amount, type, category, description=None):
    """Добавляет транзакцию"""
    conn = get_connection()
    if not conn:
        return None, "Ошибка подключения к БД"

    cursor = conn.cursor()

    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return None, "Пользователь не найден"

        query = """
            INSERT INTO transactions (user_id, amount, type, category, description) 
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (user_id, amount, type, category, description)

        cursor.execute(query, values)
        conn.commit()

        return cursor.lastrowid, None

    except Exception as e:
        return None, str(e)
    finally:
        cursor.close()
        conn.close()


def get_balance_api(user_id):
    """Возвращает баланс пользователя"""
    conn = get_connection()
    if not conn:
        return None, "Ошибка подключения к БД"

    cursor = conn.cursor()

    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None, "Пользователь не найден"

        # Считаем доходы
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = %s AND type = 'income'
        """,
            (user_id,),
        )
        income = cursor.fetchone()[0]

        # Считаем расходы
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = %s AND type = 'expense'
        """,
            (user_id,),
        )
        expense = cursor.fetchone()[0]

        balance = income - expense

        return {
            "user_id": user_id,
            "user_name": user[0],
            "balance": float(balance),
            "income": float(income),
            "expense": float(expense),
        }, None

    except Exception as e:
        return None, str(e)
    finally:
        cursor.close()
        conn.close()


def get_transactions_api(user_id, limit=10):
    """Возвращает список транзакций"""
    conn = get_connection()
    if not conn:
        return None, "Ошибка подключения к БД"

    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, amount, type, category, description, created_at 
            FROM transactions 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """,
            (user_id, limit),
        )

        transactions = cursor.fetchall()

        result = []
        for t in transactions:
            result.append(
                {
                    "id": t[0],
                    "amount": float(t[1]),
                    "type": t[2],
                    "category": t[3],
                    "description": t[4],
                    "date": str(t[5]),
                }
            )

        return result, None

    except Exception as e:
        return None, str(e)
    finally:
        cursor.close()
        conn.close()


# API Endpoints
@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Finance Manager API",
            "endpoints": {
                "POST /user": "Создать пользователя (name, email)",
                "POST /transaction": "Добавить транзакцию",
                "GET /balance/<user_id>": "Получить баланс",
                "GET /transactions/<user_id>": "Получить транзакции",
            },
        }
    )


@app.route("/user", methods=["POST"])
def create_user():
    """Создание нового пользователя"""
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Не указаны name или email"}), 400

    user_id, error = add_user_api(data["name"], data["email"])

    if error:
        return jsonify({"error": error}), 400

    return (
        jsonify(
            {
                "message": "Пользователь создан",
                "user_id": user_id,
                "name": data["name"],
                "email": data["email"],
            }
        ),
        201,
    )


@app.route("/transaction", methods=["POST"])
def create_transaction():
    """Добавление транзакции"""
    data = request.get_json()

    required = ["user_id", "amount", "type", "category"]
    if not all(k in data for k in required):
        return jsonify({"error": "Не указаны обязательные поля"}), 400

    if data["type"] not in ["income", "expense"]:
        return jsonify({"error": "type должен быть income или expense"}), 400

    transaction_id, error = add_transaction_api(
        data["user_id"],
        data["amount"],
        data["type"],
        data["category"],
        data.get("description"),
    )

    if error:
        return jsonify({"error": error}), 400

    return (
        jsonify({"message": "Транзакция добавлена", "transaction_id": transaction_id}),
        201,
    )


@app.route("/balance/<int:user_id>", methods=["GET"])
def get_balance(user_id):
    """Получение баланса"""
    balance, error = get_balance_api(user_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(balance)


@app.route("/transactions/<int:user_id>", methods=["GET"])
def get_transactions(user_id):
    """Получение списка транзакций"""
    limit = request.args.get("limit", 10, type=int)

    transactions, error = get_transactions_api(user_id, limit)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(
        {"user_id": user_id, "count": len(transactions), "transactions": transactions}
    )


if __name__ == "__main__":
    print("🚀 Запуск Finance Manager API...")
    print("📝 Доступные endpoints:")
    print("   POST /user")
    print("   POST /transaction")
    print("   GET /balance/<user_id>")
    print("   GET /transactions/<user_id>")
    print("\n🌐 Сервер запущен на http://127.0.0.1:5000")
    app.run(debug=True)
