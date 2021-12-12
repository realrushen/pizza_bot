from transitions import Machine
from transitions.core import Enum


class States(Enum):
    SIZE = 1
    PAYMENT_METHOD = 2
    ACKNOWLEDGEMENT = 3
    ACCEPTED = 4


transitions = [
    ['ask_for_payment_method', States.SIZE, States.PAYMENT_METHOD],
    ['confirm_order', States.PAYMENT_METHOD, States.ACKNOWLEDGEMENT],
    ['thank_user', States.ACKNOWLEDGEMENT, States.ACCEPTED],
    ['reset', States.ACKNOWLEDGEMENT, States.SIZE],

]

if __name__ == '__main__':
    machine = Machine(states=States, transitions=transitions, initial=States.SIZE)