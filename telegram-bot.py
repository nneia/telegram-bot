from typing import Final

# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import aiohttp

print('Starting up bot...')

TOKEN: Final = ''
BOT_USERNAME: Final = ''

# Create an empty dictionary to store user responses
user_responses = {}

# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет❗️' + "\n" + 'Перед началом ответьте пожалуйста на несколько простых вопросов: ' 
                                    + "\n" + "\n" +
                                    '1. Как вас зовут?' + 
                                    "\n" + '2. Сколько вам лет?' + 
                                    "\n" + '3. С какого вы города?' +
                                    "\n" + '4. Расскажите о вашем бизнесе или идеи (если есть инстаграм/сайт прикрепите ссылку)' + 
                                    "\n" + '5. Почему вы хотите вступить в наше коммьюнити?' +
                                    "\n" + "\n" + 'Как закончите, напишите команду "/end"'
                                    )


# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


# Lets us use the /custom command
async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_responses:
        response = format_user_responses(user_responses[user_id]) 
        await update.message.reply_text('Спасибо за ваш ответ, мы обработаем его и добавим вас в группу.')
        await send_reply('YinYang33', response)
        
    else:
        await update.message.reply_text('Вы еще не отправили ответы.')

async def send_reply(username, response):
    token = ''
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    # Get the chat ID associated with the username
    chat_id = -954189449
    print(chat_id)

    if chat_id is not None:
        params = {
            'chat_id': chat_id,
            'text': response
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    print('Reply sent successfully.')
                else:
                    print('Failed to send reply.')
    else:
        print(f'Unable to find chat ID for username: {username}')

async def get_chat_id(username):
    token = ''
    url = f'https://api.telegram.org/bot{token}/getUpdates'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                for result in data['result']:
                    if 'message' in result and 'username' in result['message']['chat']:
                        if result['message']['chat']['username'] == username:
                            chat_id = result['message']['chat']['id']
                            return chat_id
                return None
            else:
                return None




def handle_response(update):
    message = update.message
    text = message.text
    user_id = message.from_user.id

    # Check if the user already has previous responses
    if user_id in user_responses:
        user_responses[user_id]['responses'].append(text)
    else:
        user_responses[user_id] = {
            'name': message.from_user.first_name,
            'telegram': '@' + message.from_user.username,
            'responses': [text]
        }
def format_user_responses(user_responses):
    formatted_text = ""
    formatted_text += f"Имя: {user_responses['name']}\n"
    formatted_text += f"Телеграм: {user_responses['telegram']}\n"
    formatted_text += "Ответы:\n"
    for response in user_responses['responses']:
        formatted_text += f"- {response}\n"
    return formatted_text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            update.message.text = new_text  # Update the message text
            handle_response(update)
        else:
            return
    else:
        handle_response(update)

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('end', end_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=5)