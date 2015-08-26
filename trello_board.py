from trello import TrelloApi
from config import *
from messages import *

trello = TrelloApi(TRELLO_APP_KEY)
trello.set_token(TRELLO_TOKEN)
board = trello.boards.get(board_id=TRELLO_MOSCOW_BOARD_ID)
standart_list = trello.lists.get(TRELLO_STANDART_LIST_ID)
vegetable_list = trello.lists.get(TRELLO_VEGETABLE_LIST_ID)
light_list = trello.lists.get(TRELLO_LIGHT_LIST_ID)


def add_card(order, user):
    if order.cuisine == CLASSIC:
        list = TRELLO_STANDART_LIST_ID
    elif order.cuisine == VEGETABLE:
        list = TRELLO_VEGETABLE_LIST_ID
    else:
        list = TRELLO_LIGHT_LIST_ID
    trello.lists.new_card(
        list,
        TRELLO_CARD_NAME % (order.persons_count, order.dinners_count),
        TRELLO_CARD_DESCRIPTION % (
            user.city,
            user.address,
            user.name,
            user.phone
        )
    )
