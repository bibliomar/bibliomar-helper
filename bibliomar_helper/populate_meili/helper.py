# Some methods are extracted from bibliomar-scraper.
# https://github.com/bibliomar/bibliomar-scrapper/blob/main/services/search/search_service.py


import json
from unittest import result
from hurry.filesize import size, alternative
from pydantic import ValidationError
from bibliomar_helper.populate_meili.config import connect_to_sqlite
from bibliomar_helper.populate_meili.model import SearchEntry
from meilisearch import Client


@staticmethod
def bytes_to_size(size_to_convert: int | str):
    if size_to_convert is None or int(size_to_convert) == 0:
        return "0 B"

    return size(int(size_to_convert), system=alternative)


@staticmethod
def resolve_cover_url(topic: str, cover_ref: str | None):
    libgen_fiction_base = "https://libgen.is/fictioncovers"
    libgen_scitech_base = "https://libgen.is/covers"

    if cover_ref is None:
        return cover_ref

    if topic == "fiction":
        cover_url = f"{libgen_fiction_base}/{cover_ref}"

    else:
        cover_url = f"{libgen_scitech_base}/{cover_ref}"

    return cover_url


def results_to_entries(topic: str, result_set: list[dict] | tuple[dict]) -> list[dict]:
    models_list: list[dict] = []

    # Keys of elements that, if None or empty should invalidate an entry.
    # These are the MD5, title, and authors indexes, respectively.
    required_elements_keys = ["MD5", "Title", "Author"]

    for result in result_set:
        invalid_element = False

        for [k, v] in result.items():
            if k in required_elements_keys:

                if v is None or v.strip() == "":
                    invalid_element = True
                    break
            else:
                if v is None or v == "":
                    result[k] = None

        if invalid_element:
            continue

        result_as_model = {
            "authors": result.get("Author"),
            "title": result.get("Title"),
            "md5": result.get("MD5"),
            "topic": topic,
            "language": result.get("Language"),
            "extension": result.get("Extension"),
            "size": bytes_to_size(result.get("Filesize")),  # type: ignore
            "cover_url": resolve_cover_url(topic, result.get("Coverurl")),
        }

        models_list.append(result_as_model)

    return models_list


def get_current_offset():
    sqlite_conn = connect_to_sqlite()
    with sqlite_conn as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM offset ORDER BY date DESC LIMIT 1")
        results = cursor.fetchone()

    if results is None or not bool(results):
        return {"fiction": 0, "scitech": 0}
    else:
        return {
            "fiction": results[0],
            "scitech": results[1],
        }


def save_current_offset(topic: str, new_offset: int):
    current_offset = get_current_offset()
    current_offset[topic] = new_offset

    sqlite_conn = connect_to_sqlite()
    with sqlite_conn as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO offset (fiction, scitech) VALUES (?, ?)",
            (current_offset["fiction"], current_offset["scitech"]),
        )
