import json


def get_films(
    file_path: str = "data.json", film_id: int | None = None
) -> list[dict] | dict:
    with open(file_path, "r") as fp:
        data = json.load(fp)
        films = data["films"]
        if film_id != None and film_id < len(films):
            return films[film_id]
        return films


def add_film(new_film):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data["films"].append(new_film)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def delete_film(film_name):
    # 1. Read
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Modify: Rebuild the list excluding the film with the matching name
    original_count = len(data["films"])
    data["films"] = [f for f in data["films"] if f["name"].lower() != film_name.lower()]

    # 3. Write (Only save if something was actually removed)
    if len(data["films"]) < original_count:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True  # Successfully deleted

    return False  # Film not


def update_film_rating(film_name, new_rating):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Find the film and update it
    found = False
    for film in data["films"]:
        if film["name"].lower() == film_name.lower():
            film["rating"] = new_rating
            found = True
            break

    if found:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    return False
