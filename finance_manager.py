from db import get_connection


def add_user(name, email):
    """Добавляет нового пользователя"""
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        values = (name, email)

        cursor.execute(query, values)
        conn.commit()

        print(f"✅ Пользователь {name} добавлен с ID: {cursor.lastrowid}")
        return cursor.lastrowid

    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def add_transaction(user_id, amount, type, category, description=None):
    """Добавляет транзакцию"""
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            print(f"❌ Пользователь с ID {user_id} не найден")
            return False

        query = """
            INSERT INTO transactions (user_id, amount, type, category, description) 
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (user_id, amount, type, category, description)

        cursor.execute(query, values)
        conn.commit()

        print(f"✅ Транзакция добавлена с ID: {cursor.lastrowid}")
        return cursor.lastrowid

    except Exception as e:
        print(f"❌ Ошибка при добавлении транзакции: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_balance(user_id):
    """Возвращает баланс пользователя (доходы - расходы)"""
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor()

    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return None

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

        print(f"\n💰 Баланс пользователя {user[0]}: {balance} руб.")
        print(f"   Доходы: {income} руб.")
        print(f"   Расходы: {expense} руб.")

        return balance

    except Exception as e:
        print(f"❌ Ошибка при подсчете баланса: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def get_transactions(user_id, limit=10):
    """Показывает последние транзакции пользователя"""
    conn = get_connection()
    if not conn:
        return None

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

        if not transactions:
            print(f"\n📭 У пользователя нет транзакций")
            return []

        print(f"\n📊 Последние транзакции:")
        print("-" * 80)
        for t in transactions:
            sign = "+" if t[2] == "income" else "-"
            print(
                f"ID: {t[0]} | {sign}{t[1]} руб. | {t[3]} | {t[4] or 'без описания'} | {t[5]}"
            )
        print("-" * 80)

        return transactions

    except Exception as e:
        print(f"❌ Ошибка при получении транзакций: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=== Тестирование функций ===\n")

    # Добавим тестового пользователя
    user_id = add_user("Тестовый", "test@mail.ru")

    if user_id:
        # Добавим тестовые транзакции
        add_transaction(user_id, 50000.00, "income", "зарплата", "Зарплата за месяц")
        add_transaction(user_id, 3500.50, "expense", "продукты", "Пятерочка")
        add_transaction(user_id, 1200.00, "expense", "транспорт", "Проездной")
        add_transaction(user_id, 2000.00, "expense", "кафе", "Кофе с друзьями")

        # Проверим баланс
        get_balance(user_id)

        # Покажем транзакции
        get_transactions(user_id)
