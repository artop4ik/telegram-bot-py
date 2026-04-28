# Standard library
import asyncio
import logging
import os
import sys
import os
# Aiogram
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, URLInputFile

# Local
from bot_keyboards import FilmCallback, films_keyboard_markup
from commands import BOT_COMMANDS, FILM_CREATE_COMMAND, FILMS_COMMAND
from config import BOT_TOKEN as TOKEN
from data import add_film, delete_film, get_films, update_film_rating
from models import Film

# ---------------- ROUTER ----------------
router = Router()


# ---------------- STATES ----------------
class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()


class MovieStates(StatesGroup):
    search_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()


class MovieRatingStates(StatesGroup):
    rate_query = State()
    set_rating = State()


logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


@router.errors()
async def errors_handler(event):
    logging.error(f"Ошибка: {event.exception}")


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 🎬\n"
        "Я бот для фільмів. Напиши /films щоб подивитись список фільмів."
    )


# ---------------- RECOMMEND ----------------
@router.message(Command("recommend_movie"))
async def recommend_movie(message: Message):
    films = get_films()
    rated_films = [f for f in films if f.get("rating") is not None]

    if rated_films:
        recommended = max(rated_films, key=lambda f: f["rating"])
        await message.answer(
            f"Рекомендуємо переглянути: {recommended['name']} - \n"
            f"{recommended['description']} (Рейтинг: {recommended['rating']})"
        )
    else:
        await message.answer("Немає фільмів з рейтингом для рекомендації.")


# ---------------- SEARCH MOVIE ----------------
@router.message(Command("search"))
async def search_movie(message: Message, state: FSMContext):
    await message.answer("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)


@router.message(MovieStates.search_query)
async def process_search(message: Message, state: FSMContext):
    query = message.text.lower()
    films = get_films()

    found = [f for f in films if query in f["name"].lower()]

    if found:
        for film in found:
            await message.answer(f"{film['name']} - {film['description']}")
    else:
        await message.answer("Нічого не знайдено.")

    await state.clear()


# ---------------- RATE MOVIE ----------------
@router.message(Command("rate"))
async def rate_movie(message: Message, state: FSMContext):
    await message.answer("Введіть назву фільму, щоб оцінити:")
    await state.set_state(MovieRatingStates.rate_query)


# STEP 1: Get the name
@router.message(MovieRatingStates.rate_query)
async def get_rate_query(message: Message, state: FSMContext):
    film_name = message.text.lower()
    films = get_films("data.json")
    exists = any(f["name"].lower() == film_name for f in films)
    if exists:
        # Save the name in the state so we remember it for step 2
        await state.update_data(chosen_film=film_name)
        await message.answer("Фільм знайдено! Введіть оцінку (від 1 до 10):")
        await state.set_state(MovieRatingStates.set_rating)
    else:
        await message.answer("Такого фільму немає в списку.")
        await state.clear()


@router.message(MovieRatingStates.set_rating)
async def process_rating(message: Message, state: FSMContext):
    try:
        rating = int(message.text)
        if not (1 <= rating <= 10):
            raise ValueError
    except ValueError:
        await message.answer("Будь ласка, введіть число від 1 до 10.")
        return

    data = await state.get_data()
    film_name = data["chosen_film"]

    update_film_rating(film_name, rating)

    await message.answer(f"Рейтинг '{film_name}' оновлено на {rating}!")
    await state.clear()


# ---------------- FILTER MOVIES ----------------
@router.message(Command("filter"))
async def filter_movies(message: Message, state: FSMContext):
    await message.answer("Введіть жанр або рейтинг:")
    await state.set_state(MovieStates.filter_criteria)


@router.message(MovieStates.filter_criteria)
async def get_filter(message: Message, state: FSMContext):
    criteria = message.text.strip()
    films = get_films()
    filtered = []
    try:
        rating_value = float(criteria)
        for f in films:
            try:
                if float(f.get("rating", 0)) >= rating_value:
                    filtered.append(f)
            except (ValueError, TypeError):
                pass
    except ValueError:
        for f in films:
            if criteria.lower() in f.get("genre", "").lower():
                filtered.append(f)

    if filtered:
        for film in filtered:
            await message.answer(f"{film['name']} - {film['description']}")
    else:
        await message.answer("Нічого не знайдено.")

    await state.clear()


# ---------------- DELETE MOVIE ----------------
@router.message(Command("delete"))
async def delete_movie(message: Message, state: FSMContext):
    await message.answer("Введіть назву фільму для видалення:")
    await state.set_state(MovieStates.delete_query)


@router.message(MovieStates.delete_query)
async def delete_movie_process(message: Message, state: FSMContext):
    # Do NOT assign get_films() to a variable here if you don't need it
    # Just call the function directly!

    film_name = message.text

    success = delete_film(film_name)

    if success:
        await message.answer(f"Фільм '{film_name}' видалено.")
    else:
        await message.answer("Фільм не знайдено.")

    await state.clear()


# ---------------- FILM CREATE (FSM) ----------------
@router.message(FILM_CREATE_COMMAND)
async def film_create(message: Message, state: FSMContext):
    await state.set_state(FilmForm.name)
    await message.answer("Введіть назву фільму:", reply_markup=ReplyKeyboardRemove())


@router.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext):
    if not message.text or message.text.isdigit():
        await message.answer("Назва має бути текстом")
        return
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer("Введіть опис:")


@router.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Опис не може бути пустим")
        return
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.rating)
    await message.answer("Вкажіть рейтинг 0-10:")


@router.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext):
    try:
        rating = float(message.text)
        if rating < 0 or rating > 10:
            raise ValueError
    except:
        await message.answer("Введіть число від 0 до 10")
        return

    await state.update_data(rating=rating)
    await state.set_state(FilmForm.genre)
    await message.answer("Введіть жанр:")


@router.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Жанр має бути текстом")
        return
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.actors)
    await message.answer("Актори через ', ':")


@router.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Введіть хоча б одного актора")
        return

    actors = message.text.split(", ")
    if len(actors) == 0:
        await message.answer("Невірний формат. Приклад: Actor1, Actor2")
        return

    await state.update_data(actors=actors)
    await state.set_state(FilmForm.poster)
    await message.answer("Посилання на постер:")


@router.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext):
    if not message.text.startswith("http"):
        await message.answer("Введіть коректне посилання")
        return

    data = await state.update_data(poster=message.text)

    film = Film(**data)
    add_film(film.model_dump())

    await state.clear()
    await message.answer(f"Фільм {film.name} додано!")


# ---------------- FILM LIST ----------------
@router.message(FILMS_COMMAND)
async def films_list(message: Message):
    data = get_films()
    markup = films_keyboard_markup(films_list=data)

    await message.answer("Список фільмів:", reply_markup=markup)


# ---------------- CALLBACK ----------------
@router.callback_query(FilmCallback.filter())
async def film_callback(callback: CallbackQuery, callback_data: FilmCallback):
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = (
        f"Фільм: {film.name}\n"
        f"Опис: {film.description}\n"
        f"Рейтинг: {film.rating}\n"
        f"Жанр: {film.genre}"
    )

    await callback.message.answer_photo(photo=URLInputFile(film.poster), caption=text)


# ---------------- ECHO ----------------
@router.message()
async def echo(message: Message):
    text = message.text.lower()

    if text == "привіт":
        await message.answer(f"Привіт, {message.from_user.first_name}!")
    elif text == "id":
        await message.answer(f"ID: {message.from_user.id}")
    else:
        await message.answer("Я не зрозумів ")


# ---------------- MAIN ----------------
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
