import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters
from transitions import Machine

from statemachine import States, transitions


# Constants
BIG = 'Большую'
SMALL = 'Маленькую'
SIZE = 'size'
CASH = 'Наличные'
CREDIT_CARD = 'Карта'
YES = 'Да'
NO = 'Нет'


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update: Update, context: CallbackContext):
    """Starts the conversation and asks the user about pizza size."""
    context.chat_data['machine'] = Machine(states=States, transitions=transitions, initial=States.SIZE)
    context.chat_data['new_order_started'] = True

    reply_keyboard = [[BIG, SMALL]]
    update.message.reply_text(
        f'Какую вы хотите пиццу? {BIG} или {SMALL}?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=f'{BIG} или {SMALL}'
        ),
    )


def ask_for_payment_method(update: Update, context: CallbackContext):
    machine = context.chat_data['machine']
    if machine.is_SIZE() and context.chat_data['new_order_started']:
        context.chat_data[SIZE] = update.message.text
        machine.ask_for_payment_method()

        reply_keyboard = [[CASH, CREDIT_CARD]]
        update.message.reply_text(
            'Как вы будете платить??',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=f'{CASH} или {CREDIT_CARD}'
            ),
        )


def confirm_order(update: Update, context: CallbackContext):
    machine = context.chat_data['machine']
    if machine.is_PAYMENT_METHOD():
        reply_keyboard = [[YES, NO]]
        size = context.chat_data.get(SIZE)
        payment_method = update.message.text
        machine.confirm_order()

        confirmation_text = f'Вы хотите {size} пиццу, оплата - {payment_method}?'
        update.message.reply_text(
            confirmation_text,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=f'{YES} или {NO}'
            ),
        )


def thank_client(update: Update, context: CallbackContext):
    machine = context.chat_data['machine']
    if machine.is_ACKNOWLEDGEMENT() and update.message.text == NO:
        machine.reset()
        return start(update, context)
    elif machine.is_ACKNOWLEDGEMENT() and update.message.text == YES:
        update.message.reply_text('Спасибо за заказ')
        context.chat_data['new_order_started'] = False
        machine.reset()


def main():
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex(fr'^({BIG}|{SMALL})$'), ask_for_payment_method))
    dispatcher.add_handler(MessageHandler(Filters.regex(fr'^({CASH}|{CREDIT_CARD})$'), confirm_order))
    dispatcher.add_handler(MessageHandler(Filters.regex(fr'^({YES}|{NO})$'), thank_client))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
