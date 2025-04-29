from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    WELCOME=State()
    MY_DATA = State()
    CONTACTS = State()
    MY_SESSIONS = State()
    TICKETS = State()

    # ORDER_IS_DELIVERY = State()
    # ORDER_PHONE = State()
    # ORDER_NAME = State()
    # ORDER_GEO = State()
    # ORDER_EXACT_GEO = State()
    # ORDER_PAY_BONUS = State()
    # ORDER_ACCEPT = State()

    # ORDER_SHOW = State()
    # ORDER_STATUS_CHANGE = State()
    # EMPTY_ORDER_LIST = State()
    # DELIVERY_ORDER = State()
    # ORDER_END = State()
    # ORDER_WRITE_TOKEN = State()
