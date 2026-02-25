import mysql.connector

# Список паролей, которые чаще всего используются
passwords_to_try = [
    '',           # пустой пароль
    'root',       # root
    'drb2002',   # password
    'Drb2002',     # 123456
    'Drb2002014',      # mysql
    'Drb2002014@',      # admin
    'Mr224226450',       # 1234
    '@@@@@581326',        # 123
    '1',          # 1
    'admin123',   # admin123
    'root123',    # root123
    'password123' # password123
]

print("Пробуем разные пароли...\n")

for password in passwords_to_try:
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password,
            connection_timeout=5  # таймаут 5 секунд
        )
        print(f"✅ ПОДОШЕЛ пароль: '{password}'")
        conn.close()
        break
    except mysql.connector.Error as err:
        if "Access denied" in str(err):
            print(f"❌ Не подошел: '{password}'")
        else:
            print(f"⚠️ Другая ошибка с паролем '{password}': {err}")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")

print("\nПроверка завершена!")