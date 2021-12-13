import pytest
from ..pizza_order import PizzaOrder
from ..statemachine import States

@pytest.fixture()
def empty_pizza_order():
    return PizzaOrder()


def test_attributes(empty_pizza_order):

    # test object initially empty
    assert empty_pizza_order.size is None
    assert empty_pizza_order.payment_method is None


    # test can set value to size attribute
    empty_pizza_order.size = 'Big'
    assert empty_pizza_order.size == 'Big'

    # test can set value to payment_method attribute
    empty_pizza_order.payment_method = 'Card'
    assert empty_pizza_order.payment_method == 'Card'

    # test is_size_filled attribute
    assert empty_pizza_order.is_size_filled is True

    # test is_payment_method_filled attribute
    assert empty_pizza_order.is_payment_method_filled is True

def test_ask_for_payment_method(empty_pizza_order):

    # test initial state is States.SIZE
    assert empty_pizza_order.state == States.SIZE

    empty_pizza_order.ask_for_payment_method()

    # test that after calling transition ask_for_payment_method state is same
    assert empty_pizza_order.state == States.SIZE


    empty_pizza_order.size = 'Big'
    empty_pizza_order.ask_for_payment_method()

    # test that after filling size attribute and calling transition ask_for_payment_method
    # state changed to States.PAYMENT_METHOD
    assert empty_pizza_order.state == States.PAYMENT_METHOD


