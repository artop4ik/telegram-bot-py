from aiogram.filters import Command
from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand


FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')

FILMS_BOT_COMMAND = BotCommand(command='films', description="Перегляд списку фільмів")
START_BOT_COMMAND = BotCommand(command='start', description="Почати розмову")
SEARCH_BOT_COMMAND = BotCommand(command='search', description="Пошук фільму за назвою")
DELETE_BOT_COMMAND = BotCommand(command='delete', description="Видалити фільм за назвою")
RATE_BOT_COMMAND = BotCommand(command='rate', description="Поставити рейтинг фільму за назвою")
FILM_CREATE_COMMAND = Command("create_film")
...
BOT_COMMANDS = [
   BotCommand(command="films", description="Перегляд списку фільмів"),
   BotCommand(command="start", description="Почати розмову"),
   BotCommand(command="create_film", description="Додати новий фільм"),
   BotCommand(command="search", description="Пошук фільму за назвою"),
   BotCommand(command="rate", description="Поставити рейтинг фільму за назвою"),
   BotCommand(command="delete", description="Видалити фільм"),
   BotCommand(command="filter", description="відфільтрувати фільми"),
   BotCommand(command="recommend_movie", description="Рекомендації фільмів"),
]