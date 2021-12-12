from transitions import Machine

from statemachine import States


class PizzaOrder:
    def __init__(self, size=None, payment_method=None):
        self._size: str = size
        self._payment_method: str = payment_method
        self._confirmed: bool = None

        # Initially we start from asking for size state
        self.machine = Machine(self, states=States, initial=States.SIZE)
        # We don't change state until we don't get pizza size
        self.machine.add_transition(
            trigger='ask_for_payment_method',
            source=States.SIZE,
            dest=States.PAYMENT_METHOD,
            conditions=['is_size_filled']
        )
        # We don't change state until we don't get payment method
        self.machine.add_transition(
            trigger='confirm_order',
            source=States.PAYMENT_METHOD,
            dest=States.ACKNOWLEDGEMENT,
            conditions=['is_payment_method_filled']
        )
        # We do not give thanks for an order until the user has confirmed it
        self.machine.add_transition(
            trigger='thank_user',
            source=States.ACKNOWLEDGEMENT,
            dest=States.ACCEPTED,
            conditions=['is_confirmed'],

        )

    @property
    def size(self):
        return self._size

    @property.setter
    def size(self, value):
        self._size = value

    @property
    def payment_method(self):
        return self._payment_method

    @property.setter
    def payment_method(self, value):
        self._payment_method = value

    @property
    def is_filled(self):
        return self._size and self._payment_method

    @property
    def is_size_filled(self):
        return bool(self._size)

    @property
    def is_payment_method_filled(self):
        return bool(self._payment_method)

    @property
    def is_confirmed(self):
        return self._confirmed

    def confirm(self):
        self._confirmed = True
