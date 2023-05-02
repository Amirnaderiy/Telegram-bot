# -*- coding: utf-8 -*-
"""
Created on Tue May  2 14:43:48 2023

@author: Asus
"""

import logging
import telegram.ext 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import filters
from telegram.ext import Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import CallbackContext
from queue import Queue
from telegram import Update
from telegram.ext import CallbackContext
import telebot
import spacy

# load the English language model for spaCy
nlp = spacy.load('en_core_web_sm')
bot = telebot.TeleBot('6186938893:AAHe6kevF0EJ7_PhxljTCeCuYET-qXfQ4Jk')

# Replace with your channel username
channel_username = 'https://t.me/+l_rh5lMtoe1hZTE8'
user_feedback = {}

class TVSeriesPersianBot:
    def __init__(self, token):
        # Initialize the bot with given token
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Add handlers for commands and messages
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("search", self.search))
        self.dispatcher.add_handler(MessageHandler(filters.Filters.text & ~filters.Filters.command, self.handle_message))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_callback))

        # Start the bot
        self.updater.start_polling()

    def start(self, update: Update, context: CallbackContext):
        # Send the welcome message and menu
        text = "به بات خوره های سریال خوش اومدید!\n\n"\
               "#دانلود_سریال 📺\n"\
               "#دانلود_فیلم 🎞\n"\
               "#دانلود_انیمیشن 🧸\n"\
               "#دانلود_مستند 🌱\n\n"\
               "یک گزینه را انتخاب کنید:"
        keyboard = [
            [InlineKeyboardButton("دانلود فیلم و سریال", callback_data='1')],
            [InlineKeyboardButton("پیشنهاد یا انتقاد", callback_data='2')],
            [InlineKeyboardButton("درخواست فیلم یا سریال", callback_data='3')],
            [InlineKeyboardButton("عضویت در کانال و پیج اینستاگرام", callback_data='4')],
            [InlineKeyboardButton("قطع ارتباط", callback_data='5')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text=text, reply_markup=reply_markup)

    
    def search(self, message):
        if not message.text.startswith('/search '):
            bot.reply_to(message, 'Invalid command.')
            return
        query = message.text.split(' ')[1:]
        if not query:
            bot.reply_to(message, 'Please specify a search query.')
            return
        corrected_query = [nlp(word)[0]._ if nlp(word)[0].has_vector or not nlp(word)[0].is_alpha else nlp(word)[0]._.suggestions[0] if nlp(word)[0]._.suggestions else word for word in query]
        results = []
        messages = context.bot.get_chat_history(chat_id='@'+channel_username, limit=max(1, min(100, limit)))
        for msg in messages:
            if msg.document:
                file_name = msg.document.file_name
                if all(q.lower() in file_name.lower() for q in corrected_query):
                    results.append((file_name, msg.document.file_unique_id))
        if not results:
            bot.reply_to(message, 'No results found.')
            return
        reply_text = 'Search results:'
        for result in results:
            reply_text += f'\n{result[0]} /get_{result[1]}'
        bot.reply_to(message, reply_text)


    def feedback(update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
    
        # Check user state
        state = context.user_data.get('state')
    
        if state == 'WAIT_SUGGESTION':
            # Send suggestion message to admin and notify user
            feedback = f"Suggestion from user {chat_id}:\n{update.message.text}"
            context.bot.send_message(chat_id='@amirnaderiy', text=feedback)
            update.feedback.reply_text("مرسی از نظراتت. حتماً رسیدگی میکنم")
    
            # Reset user state
            context.user_data['state'] = None
    
        elif state == 'WAIT_REQUEST':
            # Send request message to admin and notify user
            feedback = f"Request from user {chat_id}:\n{update.message.text}"
            context.bot.send_message(chat_id='@amirnaderiy', text=feedback)
            update.feedback.reply_text("ممنونم سعی میکنم هر چی سریعتر به آرشیو اضافه‌ش کنم.")
    
            # Reset user state
            context.user_data['state'] = None

    def button_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        chat_id = query.message.chat_id
        query.answer()
        
    
        if query.data == '1':
            # Send message asking for search query
            message = "لطفا نام فیلم یا سریال مورد نظر را وارد کنید:"
            self.search(update.message)
    
            # Set the callback function for handling the user's search query
            context.user_data['callback_function'] = 'handle_search'
    
        elif query.data == '2':
            # Send message for option 2 and delete previous messages
            message = "اگه پیشنهاد یا انتقادی در مورد پیج، کانال یا رباتمون داری اینجا برام بنویس"
            context.bot.send_message(chat_id=chat_id, text=message)
            context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id-1) # delete previous message
            
            # Store user chat ID for later use
            context.user_data['state'] = 'WAIT_SUGGESTION'
    
        elif query.data == '3':
            # Send message for option 3 and delete previous messages
            message = "اگه درخواست فیلم یا سریالی داری اینجا برام بنویس"
            context.bot.send_message(chat_id=chat_id, text=message)
            context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id-1) # delete previous message
    
        elif query.data == '4':
            # Send message for option 4 and delete previous messages
            message = "❤️ با عضویت در کانال و پیج اینستاگراممون میتونید از جدیدترین اخبار و حاشیه‌های دنیای سریال باخبر بشی و سریالا و فیلمای مورد علاقه‌ت رو به صورت رایگان دانلود کنی "
            context.bot.send_message(chat_id=chat_id, text=message)
            context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id-1) # delete previous message
    
        elif query.data == '5':
            message = "خداحافظ عزیزم. امیدوارم روز یا شب خوبی داشته باشی"
            context.bot.send_message(chat_id=chat_id, text=message)
            context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id-1) # delete previous message
            context.bot.stop()
            
            context.user_data['state'] = 'WAIT_REQUEST'
        
            # If query.data is 5, stop further processing of user input
            return
        
        # Check if callback_function is set and call it
        if 'callback_function' in context.user_data:
            callback_function = getattr(self, context.user_data['callback_function'], None)
            if callback_function is not None:
                callback_function(update.message, context)

if __name__ == '__main__':
    bot_token = "6186938893:AAHe6kevF0EJ7_PhxljTCeCuYET-qXfQ4Jk"
    tv_series_persian_bot = TVSeriesPersianBot(bot_token)