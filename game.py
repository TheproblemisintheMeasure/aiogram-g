import cmd
import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import Message

API_TOKEN = '5848840303:AAF6Ga-Vj4Rly7WkhgoZ0cwB7MRtEH3yoEw'

# Configure the logging system
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='log.log',
    filemode='a'
)

# Initialize bot and dispatcher
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Check if user exists in the users.txt file
    with open('users.txt', 'r') as f:
        for user in f:
            user_id, user_full_name = user.strip().split(' - ')
            if user_id == str(message.from_user.id):
                await bot.send_message(
                    chat_id=message.chat.id, 
                    text=f"Привет {user_full_name}! Хотели бы вы изменить свой псевдоним?"
                )
                # Ask for new nickname
                await bot.send_message(
                    chat_id=message.chat.id, 
                    text="Каким бы ты хотел, чтобы был твой новый никнейм?",
                )
                return

    # If user doesn't exist, ask for nickname
    await bot.send_message(
        chat_id=message.chat.id, 
        text=f"Всем привет! Давайте установим ваш никнейм. Что бы вы хотели, чтобы это было?"
    )

    # Save user id to detect changes later
    user_id = message.from_user.id
    with open('users.txt', 'a') as f:
        f.write(f"{user_id} - None\n")
    
@dp.message_handler(content_types=['p'])
async def handle_photo(message: types.Message):
    # Access the photo file ID
    photo_id = message.photo[-1].file_id

    # Do something with the photo file ID, such as sending it back to the user
    await bot.send_photo(chat_id=message.chat.id, photo=photo_id)

@dp.message_handler(content_types=['d'])
async def handle_document(message: types.Message):
    # Access the file ID
    file_id = message.document.file_id

    # Do something with the file ID, such as sending it back to the user
    await bot.send_document(chat_id=message.chat.id, document=file_id)


@dp.message_handler(commands=['ban'])
async def cmd_ban(message: types.Message):
    if message.from_user.id != 1643121103:
        await bot.send_message(
            chat_id=message.chat.id,
            text="У вас нет разрешения на использование этой команды."
        )
        return

    user_input = message.text.split()[1:]
    if len(user_input) < 2:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Недостаточно аргументов. Использование: /ban имя пользователя повторно"
        )
        return

    username = user_input[0]
    ban_term = user_input[1]

    with open('users.txt', 'r') as f:
        users = f.readlines()
    user_found = False
    for user in users:
        user_id, user_full_name = user.strip().split(' - ')
        if username == user_full_name:
            user_found = True
            user_id = int(user_id)
            break
    if not user_found:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Пользователь с именем {username} не найден."
        )
        return

    with open('banned_users.txt', 'a') as f:
        f.write(f"{user_id} - {ban_term}\n")

    await bot.send_message(
        chat_id=message.chat.id,
        text=f"User {username} banned for {ban_term}."
    )

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Список доступных команд:\n\n"
             f"/start - установить свой никнейм\n"
             f"/w <имя пользователя> <сообщение> - отправить сообщение пользователю\n"
             f"/list - показать всех пользователей\n"
             f"/help - показать это сообщение"
    )


@dp.message_handler(commands=['list'])
async def cmd_list(message: types.Message):
    with open('users.txt', 'r') as f:
        users = f.readlines()
        user_list = [user.strip().split(' - ')[1] for user in users]
        user_list = '\n'.join(user_list)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Список всех пользователей:\n{user_list}"
)

@dp.message_handler(commands=['w'])
async def cmd_write(message: types.Message):
    user_input = message.text.split()[1:]
    if len(user_input) < 2:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Недостаточно аргументов. Использование: /w <имя пользователя> <сообщение>"
        )
        return

    username = user_input[0]
    user_message = ' '.join(user_input[1:])

    with open('users.txt', 'r') as f:
        users = f.readlines()
    user_found = False
    sender_nickname = message.from_user.full_name
    for user in users:
        user_id, user_full_name = user.strip().split(' - ')
        if int(user_id) == message.from_user.id:
            sender_nickname = user_full_name
            break

    for user in users:
        user_id, user_full_name = user.strip().split(' - ')
        if username == user_full_name:
            user_found = True
            user_id = int(user_id)
            break
    if not user_found:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Пользователь с именем {username} не найден."
        )
        return

    with open('chat_users.txt', 'a', encoding='utf-8') as f:
        f.write(f"{sender_nickname} -> {username}: {user_message}\n")

    await bot.send_message(
        chat_id=user_id,
        text=f"{sender_nickname} says: {user_message}"
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Сообщение отправлено {username}."
    )

import logging

# Set up logging for each user
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger()

@dp.message_handler()
async def process_message(message: types.Message):
    with open('chat_log_all.txt', 'a', encoding='utf-8') as f:
        f.write(f"{message.from_user.full_name}: {message.text}\n")

def help_message(arguments, message):
    response = {'chat_id': message['chat']['id']}
    result = ["Hey, %s!" % message["from"].get("first_name"),
              "\rI can accept only these commands:"]
    for command in cmd:
        result.append(command)
    response['text'] = "\n\t".join(result)
    return response

@dp.message_handler()
async def check_ban(message: types.Message):
    with open('banned_users.txt', 'r') as f:
        banned_users = f.readlines()
    
    user_id = str(message.from_user.id)
    for banned_user in banned_users:
        banned_user_id, ban_term = banned_user.strip().split(' - ')
        if user_id == banned_user_id:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"Вы забанены за {ban_term}."
            )
            return

@dp.message_handler()
async def process_nickname(message: types.Message):
    with open('users.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if user exists in the file
    user_id = str(message.from_user.id)
    for i, user in enumerate(lines):
        if user.startswith(user_id):
            _, user_full_name = user.strip().split(' - ')
            if user_full_name != 'None':
                # Nickname has already been set
                return
            else:
                # Update nickname
                lines[i] = f"{user_id} - {message.text}\n"
                break
    else:
        return

    # Update users.txt file
    with open('users.txt', 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)