from random import choice

import telebot

from datetime import datetime

token = '7760290637:AAGVi4j0IN76gf_mfDsrXPlbRw60Z6xMBIE'

bot = telebot.TeleBot(token)


RANDOM_TASKS = ['Написать Гвидо письмо', 'Выучить Python', 'Записаться на курс в Нетологию', 'Посмотреть 4 сезон Рик и Морти']

todos = dict()


HELP = '''
Список доступных команд:
/show ДД.ММ.ГГГГ - напечатать все задачи на заданную дату
/add ДД.ММ.ГГГГ задача - добавить задачу на указанную дату
/done ДД.ММ.ГГГГ номер_задачи - отметить задачу выполненной
/random - добавить на сегодня случайную задачу
/help - Напечатать help
'''


def add_todo(date, task):
    # Если ключа даты нет или там не список – создаём новый список
    if date not in todos or not isinstance(todos[date], list):
        todos[date] = []
    
    # Добавляем задачу в виде словаря
    todos[date].append({'task': task, 'done': False})


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(commands=['random'])
def random(message):
    task = choice(RANDOM_TASKS)
    today = datetime.today().strftime('%d.%m.%Y')
    add_todo(today, task)
    bot.send_message(message.chat.id, f'Задача {task} добавлена на сегодня ({today})')


@bot.message_handler(commands=['add'])
def add(message):
    try:
        parts = message.text.split(maxsplit=2)  # Разделяем сообщение на три части: /add, дата, задача
        if len(parts) < 3:
            raise ValueError("Неверный формат. Используйте: /add ДД.ММ.ГГГГ задача")
        
        _, date_str, task = parts  # Разбираем команду: игнорируем /add, получаем дату и текст задачи

        # Проверяем корректность формата даты
        try:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')  # Конвертируем дату из строки в объект datetime
            date_formatted = date_obj.strftime('%d.%m.%Y')  # Переводим обратно в строку (чтобы убрать лишние пробелы)
        except ValueError:
            bot.send_message(message.chat.id, "Ошибка: Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return

         # Проверяем, что дата не в прошлом
        today = datetime.today().date()
        if date_obj.date() < today:
            bot.send_message(message.chat.id, "Ошибка: Нельзя добавлять задачи в прошлое! Укажите текущую или будущую дату.")
            return
        
        add_todo(date_formatted, task)  # Добавляем задачу
        bot.send_message(message.chat.id, f'Задача "{task}" добавлена на дату {date_formatted}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')


@bot.message_handler(commands=['show'])
def show(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            raise ValueError("Неверный формат. Используйте: /show ДД.ММ.ГГГГ")

        date_str = parts[1]

        # Проверяем формат даты
        try:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            date_formatted = date_obj.strftime('%d.%m.%Y')
        except ValueError:
            bot.send_message(message.chat.id, "Ошибка: Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return

        # Проверяем, есть ли задачи на указанную дату
        if date_formatted in todos:
            # Если по ошибке в `todos[date_formatted]` хранится строка, исправляем это
            if not isinstance(todos[date_formatted], list):
                bot.send_message(message.chat.id, "Ошибка в данных: задачи были сохранены неправильно.")
                return

            if not todos[date_formatted]:  # Если список пустой
                tasks = "На эту дату задач нет"
            else:
                tasks = '\n'.join(
                    f"{i + 1}. {'[✔]' if task.get('done') else '[ ]'} {task.get('task', 'Ошибка данных')}"
                    for i, task in enumerate(todos[date_formatted]) if isinstance(task, dict)  # Защита от ошибок
                )
        else:
            tasks = "На эту дату задач нет"

        bot.send_message(message.chat.id, tasks)
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')

@bot.message_handler(commands=['done'])
def mark_done(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            raise ValueError("Неверный формат. Используйте: /done ДД.ММ.ГГГГ номер_задачи")

        _, date_str, task_index_str = parts

        try:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            date_formatted = date_obj.strftime('%d.%m.%Y')
        except ValueError:
            bot.send_message(message.chat.id, "Ошибка: Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return

        if date_formatted not in todos or not todos[date_formatted]:
            bot.send_message(message.chat.id, "На эту дату нет задач.")
            return

        try:
            task_index = int(task_index_str) - 1  # Индексация с 0
            if task_index < 0 or task_index >= len(todos[date_formatted]):
                raise IndexError
        except (ValueError, IndexError):
            bot.send_message(message.chat.id, "Ошибка: Неверный номер задачи.")
            return

        todos[date_formatted][task_index]['done'] = True  # Отмечаем задачу как выполненную
        bot.send_message(message.chat.id, f'Задача "{todos[date_formatted][task_index]["task"]}" отмечена как выполненная.')

    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')

bot.polling(none_stop=True)