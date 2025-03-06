import os
import shutil
import sys
import json
import requests
import stashapi.log as log
from stashapi.stashapp import StashInterface

try:
    import config
except ModuleNotFoundError:
    if not os.path.exists("config.py"):
        shutil.copy("config.example", "config.py")
        print("created example config.py")
        exit(0)


def get_image_url(search_query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": config.searchPhrase(search_query),
        "cx": config.cseid,
        "key": config.api,
        "searchType": "image",
        "num": 2,
        "safe": "off",
    }
    response = requests.get(search_url, params=params)
    # print(search_url)
    response.raise_for_status()
    search_results = response.json()
    if "items" not in search_results:
        raise Exception("No images found")
    return search_results["items"][0]["link"]


def main():
    global stash
    #change per_page for how many tags to process
    t = stash.find_tags(
        filter={
            "per_page": 50,
            "page": 1,
            "sort": "scenes_count",
            "direction": "DESC"
        },
        f={
            "is_missing": "image",
            "scene_count": {
                "value": 0,
                "modifier": "GREATER_THAN"}
        })
    for tag in t:
        url = get_image_url(tag.get('name'))
        stash.update_tag(tag_update={"id": tag.get("id"), "image": url})
        # print(tag.get("name"))
        log.info(f"Set image for {tag.get("name")}")


if __name__ == "__main__":
    if "DEBUG" in os.environ:
        stash = StashInterface({
            "scheme": "https",
            "host": "localhost",
            "port": "9999",
            "logger": log,
            "ApiKey": config.stashAPI
        })
    else:
        json_input = json.loads(sys.stdin.read())
        # log.debug(json_input)
        FRAGMENT_SERVER = json_input.get("server_connection")
        stash = StashInterface(FRAGMENT_SERVER)
    main()
