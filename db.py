import mysql.connector
from mysql.connector import Error


def get_connection():
    """Создает и возвращает подключение к базе данных"""
    try:
        connection = mysql.connector.connect(
            host="localhost",  # твой MySQL сервер
            database="finance_db",  # имя базы данных
            user="root",  # твой пользователь MySQL
            password="Drb2002014",  # твой пароль MySQL (оставь '', если нет пароля)
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения к базе: {e}")
        return None


def test_connection():
    """Проверяет, работает ли подключение"""
    conn = get_connection()
    if conn:
        print("✅ Подключение к базе успешно!")
        conn.close()
        return True
    else:
        print("❌ Не удалось подключиться к базе")
        return False


# Если запустить этот файл отдельно, проверим подключение
if __name__ == "__main__":
    test_connection()
