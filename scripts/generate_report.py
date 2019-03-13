from config import *
import requests
import pprint

from match import Match

from os import listdir, mkdir
from os.path import isfile, join, dirname, abspath
import json

pp = pprint.PrettyPrinter(indent=2)


def get_matches():
    matches = []
    matches_d = dirname(abspath(__file__)) + \
        "/match_data"

    for match in listdir(matches_d):
        with open(matches_d + "/" + match) as m:
            matches.append(json.load(m))

    return matches


def update_match_results_helper(report, status, team):
    for s in team:
        r_s = report['summoners']
        if r_s.get(s, None) != None:
            if r_s[s].get(status):
                r_s[s][status] += 1
            else:
                r_s[s][status] = 1

            if r_s[s].get('games played'):
                r_s[s]['games played'] += 1
            else:
                r_s[s]['games played'] = 1

            if r_s[s].get('won', 0) > 0:
                r_s[s]['win rate'] = str(
                    r_s[s]['won']/r_s[s]['games played'] * 100) + "%"
            else:
                r_s[s]['win rate'] = 0
        else:
            r_s[s] = {}
            r_s[s][status] = 1
            r_s[s]['games played'] = 1

    return report


def update_match_results(report, winners, losers):
    report = update_match_results_helper(report, "won", winners)
    report = update_match_results_helper(report, "lost", losers)
    return report


def update_champions(report, champ_picks, bans):
    r_c = report['champions']
    r_c['total games played'] += 1

    if bans:
        for b in bans:
            c = CHAMPION_IDS[str(b)]
            if r_c['bans'].get(c):
                r_c['bans'][c]['count'] += 1
            else:
                r_c['bans'][c] = {}
                r_c['bans'][c]['count'] = 1

        for champ in r_c['bans']:
            r_c['bans'][champ]['ban rate'] = "{:.2f}%".format(
                (r_c['bans'][champ]['count'] / r_c['total games played']) * 100)

    for c_p in champ_picks:
        c_n = CHAMPION_IDS[str(c_p['champ_id'])]
        if r_c['picks'].get(c_n):
            r_c['picks'][c_n]['count'] += 1
        else:
            r_c['picks'][c_n] = {}
            r_c['picks'][c_n]['count'] = 1

    for champ in r_c['picks']:
        r_c['picks'][champ]['pick rate'] = "{:.2f}%".format(
            r_c['picks'][champ]['count'] / r_c['total games played'] * 100)

    return report


def main():
    report = {'summoners': {}, 'champions': {
        'bans': {}, 'picks': {}, 'total games played': 0}}
    for s in SUMMONERS:
        report['summoners'][s] = {}

    match_results = SUMMONERS
    champions = CHAMPION_IDS

    count = 0
    for match in get_matches():
        m = Match(match)
        print(m.match_id)
        # updates statistics for the summoner in each game
        report = update_match_results(
            report, m.get_winning_team(), m.get_losing_team())
        count += 1

        # updates the ban rates of champions and such
        pp.pprint(m.get_all_picks())
        report = update_champions(report, m.get_all_picks(), m.get_all_bans())
    pp.pprint(report)


if __name__ == "__main__":
    main()
