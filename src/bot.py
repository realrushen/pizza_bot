import logging
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters

from config import BOT_TOKEN
from pizza_order import PizzaOrder

# Constants

# Answers
BIG = 'Большую'
SMALL = 'Маленькую'
CASH = 'Наличные'
CREDIT_CARD = 'Карта'
YES = 'Да'
NO = 'Нет'

# Dict keys
PIZZA_ORDER = 'pizza_order'

# Commands
START = 'start'

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_pizza_order(update: Update, context: CallbackContext) -> Optional[PizzaOrder]:
    try:
        pizza_order = context.chat_data[PIZZA_ORDER]
    except KeyError:
        update.message.reply_text('Для заказа пиццы используйте команду /start')
        return None
    return pizza_order


def start(update: Update, context: CallbackContext) -> None:
    """Starts the conversation and asks the user about pizza size."""
    context.chat_data[PIZZA_ORDER] = PizzaOrder()

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
    pizza_order = get_pizza_order(update, context)
    if not pizza_order:
        return

    if not pizza_order.is_filled:
        # store size and trigger transition
        pizza_order.size = update.message.text
        pizza_order.trigger('ask_for_payment_method')

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
    pizza_order = get_pizza_order(update, context)
    if not pizza_order:
        return

    if pizza_order.is_size_filled:
        pizza_order.payment_method = update.message.text
        pizza_order.trigger('confirm_order')

        size = pizza_order.size
        reply_keyboard = [[YES, NO]]
        confirmation_text = f'Вы хотите {pizza_order.size} пиццу,' \
                            f' оплата - {pizza_order.payment_method}?'
        update.message.reply_text(
            confirmation_text,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                resize_keyboard=True,
                input_field_placeholder=f'{YES} или {NO}'
            ),
        )


def thank_client(update: Update, context: CallbackContext):
    pizza_order = get_pizza_order(update, context)
    if not pizza_order:
        return

    if update.message.text == YES:
        pizza_order.confirm()

    if pizza_order.trigger('thank_user'):
        update.message.reply_text('Спасибо за заказ')

        # TODO:client sensitive personal data must be masked in production
        logger.info(
            '%s, chat_id=%s, user_id=%s',
            pizza_order,
            update.message.from_user.id,
            update.message.chat.id,
        )
    else:
        return start(update, context)


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
