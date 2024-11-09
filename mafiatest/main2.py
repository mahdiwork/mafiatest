import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

TOKEN ='7018847010:AAEMTrqs7mZRwxyaXE_XUgbyYPYzl_Twt3M'
bot = telebot.TeleBot(TOKEN)


master_cid = 748626808

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        # print(m)
        if m.content_type == 'text':
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + m.text)
        elif m.content_type == 'photo':
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + "New photo recieved")
        elif m.content_type == 'document':
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + 'New Document recieved')

bot.set_update_listener(listener)



@bot.message_handler(commands=['start'])
def command_config(m): 
    if m.chat.type in ['group' , 'supergroup']:
        bot

bot.infinity_polling()