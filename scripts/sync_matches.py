from config import *
import requests
import pprint
from time import sleep

from os import listdir, mkdir
from os.path import isfile, join, dirname, abspath
import json


pp = pprint.PrettyPrinter(indent=4)


def sync_custom_match_history():
    local_match_ids = get_local_custom_match_history()
    need_to_create_locally = set(SEASON_FOUR_MATCH_IDS) - set(local_match_ids)
    for match_id in need_to_create_locally:
        request_url = RIOT_GAMES_LINK + RIOT_GET_MATCH_DETAILS + \
            str(match_id) + "?api_key=" + RIOT_API_KEY

        r = requests.get(request_url)
        if r.status_code == 200:
            print("Creating: {}.json".format(str(match_id)))
            post_local_match_history(str(match_id), r.json())
            print("Successfully downloaded and created: {}.json!\nPlease fill out the participant names on the newly created json file!".format(str(match_id)))
        else:
            print(str(match_id) + " failed: " + str(r.status_code))


def get_local_custom_match_history():
    matches = {}
    matches_d = dirname(abspath(__file__)) + \
        "/season_4"

    return [int(f.split(".")[0]) for f in listdir(
        matches_d) if isfile(join(matches_d, f))]


def post_local_match_history(match_id, match):
    matches_d = dirname(abspath(__file__)) + \
        "/season_4"
    with open('{}/{}.json'.format(matches_d, match_id), 'w') as outfile:
        json.dump(match, outfile)


if __name__ == "__main__":
    # Gets and downloads all the custom match ids for recent season in config.py
    sync_custom_match_history()
