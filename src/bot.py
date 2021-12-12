import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters
from transitions import Machine

from config import BOT_TOKEN
from statemachine import States, transitions

# Constants

# Answers
BIG = 'Большую'
SMALL = 'Маленькую'
CASH = 'Наличные'
CREDIT_CARD = 'Карта'
YES = 'Да'
NO = 'Нет'

# dict keys
SIZE = 'size'
MACHINE = 'machine'
NEW_ORDER_FLAG = 'new_order_started'
PAYMENT_METHOD = 'payment_method'

# commands
START = 'start'

# setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_state_machine(update: Update, context: CallbackContext):
    try:
        machine = context.chat_data[MACHINE]
    except KeyError:
        update.message.reply_text('Для заказа пиццы используйте команду /start')
        return None
    return machine


def start(update: Update, context: CallbackContext):
    """Starts the conversation and asks the user about pizza size."""
    context.chat_data[MACHINE] = Machine(states=States, transitions=transitions, initial=States.SIZE)
    context.chat_data[NEW_ORDER_FLAG] = True

    reply_keyboard = [[BIG, SMALL]]
    update.message.reply_text(
        f'Какую вы хотите пиццу? {BIG} или {SMALL}?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder=f'{BIG} или {SMALL}'
        ),
    )


def ask_for_payment_method(update: Update, context: CallbackContext):
    """Stores  pizza size in context.chat_data dictionary.
    Asks user about payment method and changes finite state
    machine state to States.PAYMENT_METHOD"""
    machine = get_state_machine(update, context)
    if not machine:
        return
    if machine.is_SIZE() and context.chat_data[NEW_ORDER_FLAG]:
        context.chat_data[SIZE] = update.message.text
        machine.ask_for_payment_method()

        reply_keyboard = [[CASH, CREDIT_CARD]]
        update.message.reply_text(
            'Как Вы будете платить?',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                resize_keyboard=True,
                input_field_placeholder=f'{CASH} или {CREDIT_CARD}'
            ),
        )


def confirm_order(update: Update, context: CallbackContext):
    """"""
    machine = get_state_machine(update, context)
    if not machine:
        return
    if machine.is_PAYMENT_METHOD():
        size = context.chat_data.get(SIZE)
        payment_method = update.message.text
        context.chat_data[PAYMENT_METHOD] = payment_method

        machine.confirm_order()

        reply_keyboard = [[YES, NO]]
        confirmation_text = f'Вы хотите {size} пиццу, оплата - {payment_method}?'
        update.message.reply_text(
            confirmation_text,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                resize_keyboard=True,
                input_field_placeholder=f'{YES} или {NO}'
            ),
        )


def thank_client(update: Update, context: CallbackContext):
    machine = get_state_machine(update, context)
    if not machine:
        return
    if machine.is_ACKNOWLEDGEMENT() and update.message.text == NO:
        machine.reset()
        return start(update, context)
    elif machine.is_ACKNOWLEDGEMENT() and update.message.text == YES:
        update.message.reply_text('Спасибо за заказ')
        context.chat_data[NEW_ORDER_FLAG] = False

        # client sensitive data must be masked in production
        logger.info(
            'New Order(size=%s, payment_method=%s), chat_id=%s, user_id=%s',
            context.chat_data.get(SIZE),
            context.chat_data[PAYMENT_METHOD],
            update.message.from_user.id,
            update.message.chat.id,
        )
        machine.reset()


def main():
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(START, start))
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
