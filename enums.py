from enum import Enum


class ChatStatus(Enum):
    drafted = 0
    known_phone = 1
    known_name = 2
    known_email = 3
    known_city = 5
    known_address = 4
