# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from models import User, Order
from mongoengine import DoesNotExist, Q
import phonenumbers
import telegram
import messages
from config import TELEGRAMM_TOKEN
import trello_board

LAST_UPDATE_ID = None


def start():
    global LAST_UPDATE_ID

    bot = telegram.Bot(TELEGRAMM_TOKEN)

    try:
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None

    while True:
        receive(bot)


def receive(bot):
    global LAST_UPDATE_ID

    for update in bot.getUpdates(offset=LAST_UPDATE_ID):
        chat_id = update.message.chat_id
        message = update.message.text.encode('utf-8').strip()
        user_id = update.message.from_user.id
        try:
            user = User.objects.get(user_id=user_id)
        except DoesNotExist:
            user = User(user_id=user_id)
            user.save()

        today = datetime.today()
        last_thursday = today - timedelta(days=today.weekday() + 4)
        next_thursday = today - timedelta(days=today.weekday() - 4)
        try:
            order = Order.objects.get(
                Q(user_id=user_id) |
                Q(created__gt=last_thursday) |
                Q(created__lt=next_thursday)
            )
        except DoesNotExist:
            order = Order(user_id=user_id)
            order.save()
        if "/help" in message:
            bot.sendMessage(chat_id=chat_id,
                            text=messages.HELP,
                            reply_markup=telegram.ReplyKeyboardHide)
        elif "/start" in message and not user.phone:
            bot.sendMessage(chat_id=chat_id,
                            text=messages.TELL_ME_PHONE,
                            reply_markup=telegram.ReplyKeyboardHide)
        elif "/start" in message and not order:
            bot.sendMessage(chat_id=chat_id,
                            text=messages.TELL_ME_COUNT_PERSONS,
                            reply_markup=telegram.ReplyKeyboardMarkup(
                                messages.PERSONS_CHOICES
                            ))
        else:
            if not user.phone:
                try:
                    phone = phonenumbers.parse(message, 'RU')
                    phone = phonenumbers.format_number(phone,
                                                       phonenumbers.PhoneNumberFormat.E164)
                    user.update(set__phone=phone)
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_EMAIL,
                                    reply_markup=telegram.ReplyKeyboardHide())
                except:
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_PHONE,
                                    reply_markup=telegram.ReplyKeyboardHide())
            elif not user.email:
                try:
                    user.update(set__email=message)
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_NAME,
                                    reply_markup=telegram.ReplyKeyboardHide())
                except:
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_EMAIL,
                                    reply_markup=telegram.ReplyKeyboardHide())
            elif not user.name:
                user.update(set__name=message)
                bot.sendMessage(chat_id=chat_id,
                                text=messages.TELL_ME_CITY,
                                reply_markup=telegram.ReplyKeyboardMarkup(
                                    messages.CITY_CHOICE))
            elif not user.city:
                if message == "Москва" or message == "Санкт-Петербург":
                    user.update(set__city=message)
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_ADDRESS,
                                    reply_markup=telegram.ReplyKeyboardHide())
                else:
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_CITY,
                                    reply_markup=telegram.ReplyKeyboardMarkup(
                                        messages.CITY_CHOICE))
            elif not user.address:
                user.update(set__address=message)
                bot.sendMessage(chat_id=chat_id,
                                text=messages.TELL_ME_COUNT_PERSONS,
                                reply_markup=telegram.ReplyKeyboardMarkup(
                                    messages.PERSONS_CHOICES
                                ))
            elif not order.persons_count:
                if message == '2' or message == '4':
                    try:
                        order.update(set__persons_count=int(message))
                        bot.sendMessage(chat_id=chat_id,
                                        text=messages.TELL_ME_COUNT_DINNERS,
                                        reply_markup=telegram.ReplyKeyboardMarkup(
                                            messages.DINNERS_CHOICES
                                        ))
                    except:
                        bot.sendMessage(chat_id=chat_id,
                                        text=messages.TELL_ME_COUNT_PERSONS,
                                        reply_markup=telegram.ReplyKeyboardMarkup(
                                            messages.PERSONS_CHOICES
                                        ))
                else:
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_COUNT_PERSONS,
                                    reply_markup=telegram.ReplyKeyboardMarkup(
                                        messages.PERSONS_CHOICES
                                    ))
            elif not order.dinners_count:
                if message == '5' or message == '3':
                    try:
                        order.update(set__dinners_count=int(message))
                        bot.sendMessage(chat_id=chat_id,
                                        text=messages.TELL_ME_CUISINE,
                                        reply_markup=telegram.ReplyKeyboardMarkup(
                                            messages.CUISINE_CHOICES
                                        ))
                    except:
                        bot.sendMessage(chat_id=chat_id,
                                        text=messages.TELL_ME_COUNT_DINNERS,
                                        reply_markup=telegram.ReplyKeyboardMarkup(
                                            messages.DINNERS_CHOICES
                                        ))
                else:
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_COUNT_DINNERS,
                                    reply_markup=telegram.ReplyKeyboardMarkup(
                                        messages.DINNERS_CHOICES
                                    ))
            elif not order.cuisine:
                try:
                    if message == "Классическое" or message == "Вегетарианское" or message == "Легкое":
                        order.cuisine = message
                        order.update(set__cuisine=message)
                        trello_board.add_card(order, user)
                        bot.sendMessage(chat_id=chat_id,
                                        text=messages.MAKE_ORDER,
                                        reply_markup=telegram.ReplyKeyboardHide())
                    else:
                        bot.sendMessage(chat_id=chat_id,
                                        text=messages.TELL_ME_CUISINE,
                                        reply_markup=telegram.ReplyKeyboardMarkup(
                                            messages.CUISINE_CHOICES))
                except:
                    bot.sendMessage(chat_id=chat_id,
                                    text=messages.TELL_ME_CUISINE,
                                    reply_markup=telegram.ReplyKeyboardMarkup(
                                        messages.CUISINE_CHOICES
                                    ))

            elif order.dinners_count and order.persons_count and order.cuisine:
                bot.sendMessage(chat_id=chat_id,
                                text=messages.ALREADY_HAS_ORDER,
                                reply_markup=telegram.ReplyKeyboardHide())
        LAST_UPDATE_ID = update.update_id + 1
