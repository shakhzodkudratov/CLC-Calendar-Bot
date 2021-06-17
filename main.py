import datetime
import settings
from typing import Optional

from dateutil.relativedelta import relativedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher, Filters, CallbackContext, \
    MessageHandler, CommandHandler, CallbackQueryHandler

updater = Updater(token=settings.TELEGRAM_TOKEN)
dispatcher: Dispatcher = updater.dispatcher


def month_array(date: datetime.date):
    arr = []
    month_start_date = date - relativedelta(days=date.day - 1)
    next_month_start_date = month_start_date + relativedelta(months=1)
    month_end_date = next_month_start_date - relativedelta(days=1)
    days_in_month = month_end_date.day

    before_offset = month_start_date.weekday()
    after_offset = 6 - month_end_date.weekday()

    for i in range(before_offset + days_in_month + after_offset):
        if i % 7 == 0:
            arr.append([])

        index = i - before_offset
        arr[-1].append(month_start_date + relativedelta(days=index))
    return arr


def generate_keyboard(date: Optional[datetime.date]):
    if date is None:
        date = datetime.date.today()
    prev_month_date = date - relativedelta(months=1)
    next_month_date = date + relativedelta(months=1)

    data = month_array(date)

    keyboard = [[
        InlineKeyboardButton('<', callback_data=f'date|{prev_month_date.month}'
                                                f'|{prev_month_date.year}'),
        InlineKeyboardButton(f"{date.strftime('%B')} {date.year}",
                             callback_data='?'),
        InlineKeyboardButton('>', callback_data=f'date'
                                                f'|{next_month_date.month}'
                                                f'|{next_month_date.year}'),
    ]]

    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    temp = []
    for weekday in weekdays:
        temp.append(InlineKeyboardButton(weekday, callback_data='?'))
    keyboard.append(temp)

    for row in data:
        temp = []
        for cell_date in row:
            cell_date: datetime.date = cell_date
            temp.append(
                InlineKeyboardButton(cell_date.strftime('%d'),
                                     callback_data=f'?'))
        keyboard.append(temp)

    return keyboard


def calendar_handler(update: Update, context: CallbackContext):
    keyboard = generate_keyboard(None)

    update.message.reply_text(
        'Here is it!',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


def callback_query_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data
    print(update)
    if 'date' in data:
        _, month, year = data.split('|')
        new_date = datetime.date(int(year), int(month), 1)
        keyboard = generate_keyboard(new_date)
        context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    #     update.message.edit_reply_markup(
    #         reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    #     )


def main_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Welcome!',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='/calendar')]],
            resize_keyboard=True
        )
    )


dispatcher.add_handler(CommandHandler('calendar', calendar_handler))
dispatcher.add_handler(MessageHandler(Filters.all, main_handler))
dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))

updater.start_polling()
updater.idle()
