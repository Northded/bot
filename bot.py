import mysql.connector
import requests
import json

TOKEN = '7084780283:AAFUKQ05TKuMjLXFKNJzuRGqg2dPpRZ-vbA'

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=payload)

def get_schedule_data(group):
    conn = None
    schedule_data = 'Расписание для этой группы отсутствует.'
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='cccc'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT schedule FROM schedules WHERE group_name = %s", (group,))
        result = cursor.fetchone()
        
        if result:
            schedule_data = result[0]
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
    finally:
        if conn:
            conn.close()
    
    return schedule_data

# Создание базы данных и таблицы
def create_database_table():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''
    )

    with conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS ccc")

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='ccc'
    )

    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_name VARCHAR(50) NOT NULL,
                schedule TEXT
            )
        """)

    conn.close()

def insert_schedule_data(group, schedule):
    conn = None

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='cccc'
        )
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO schedules (group_name, schedule) VALUES (%s, %s)", (group, schedule))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error inserting schedule data into database: {e}")
    finally:
        if conn:
            conn.close()

def list_groups():
    conn = None
    group_list = ""

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='cccc'
        )

        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM schedules")
        results = cursor.fetchall()

        group_list = "\n".join([row[0] for row in results])
    except mysql.connector.Error as e:
        print(f"Error listing groups from database: {e}")
    finally:
        if conn:
            conn.close()

    return group_list

# Функция обработки сообщений и запросов
def handle_message(message):
    chat_id = message['chat']['id']
    text = message.get('text', '')
    
    if '/start' in text:
        send_message(chat_id, 'Привет! Я бот! Для списка команд введите /help.')
    elif '/help' in text:
        send_message(chat_id, 'Список доступных команд:\n/start - начало чата\n/help - показать список команд\n/schedule <номер_группы> - показать расписание для группы\n/add_schedule <номер_группы> <расписание> - добавить расписание для группы\n/list_groups - показать список добавленных групп')
    elif '/schedule' in text:
        group = text.split()[-1]  # Получаем введенный номер группы
        schedule_data = get_schedule_data(group)
        send_message(chat_id, schedule_data)
    elif '/add_schedule' in text:
        commands = text.split()
        if len(commands) >= 4:
            group = commands[1]
            schedule = ' '.join(commands[2:])
            insert_schedule_data(group, schedule)
            send_message(chat_id, f'Расписание для группы {group} успешно добавлено!')
        else:
            send_message(chat_id, 'Некорректный формат команды. Используйте "/add_schedule <номер_группы> <расписание>"')
    elif '/list_groups' in text:
        group_list = list_groups()
        if group_list:
            send_message(chat_id, f'Список добавленных групп:\n{group_list}')
        else:
            send_message(chat_id, 'Список добавленных групп пуст.')
    else:
        send_message(chat_id, 'Извините, не могу понять ваш запрос. Введите /help для списка доступных команд.')

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(url, params=params)
    updates = json.loads(response.content)
    return updates.get('result', [])

def main():
    # Создание базы данных и таблицы перед началом работы
    create_database_table()

    offset = None
    while True:
        updates = get_updates(offset)

        if len(updates) > 0:
            for update in updates:
                if 'message' in update:
                    handle_message(update['message'])
                offset = update['update_id'] + 1

if __name__ == '__main__':
    main()