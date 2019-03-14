from config import *
import requests
import pprint

from match import Match
from collections import Counter

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
    r_s = report['summoners']
    for s in team:
        if r_s.get(s, None) != None:
            if not r_s[s].get(status):
                r_s[s][status] = 0
            r_s[s][status] += 1

            if not r_s[s].get('games played'):
                r_s[s]['games played'] = 0
            r_s[s]['games played'] += 1

            if r_s[s].get('won', 0) > 0:
                r_s[s]['win rate'] = "{:.2f}%".format(
                    r_s[s]['won']/r_s[s]['games played'] * 100)
            else:
                r_s[s]['win rate'] = "00.00%"
        else:
            r_s[s] = {}
            r_s[s][status] = 1
            r_s[s]['games played'] = 1

    for p1 in team:
        for p2 in team:
            if p1 != p2:
                if not r_s[p1].get('partners'):
                    r_s[p1]['partners'] = {}

                if not r_s[p1]['partners'].get(p2):
                    r_s[p1]['partners'][p2] = {
                        "won": 0, "lost": 0, "win rate": 0}

                r_s[p1]['partners'][p2][status] += 1

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


def update_summoner_picks_and_roles(report, all_picks, participants, winning_team):
    picks = merge_participants_picks_results(
        all_picks, participants, winning_team)

    r_s = report['summoners']

    for pick in picks:
        if not r_s[pick['summoner']].get('role'):
            r_s[pick['summoner']]['role'] = {}

        if not r_s[pick['summoner']]['role'].get(pick['role']):
            r_s[pick['summoner']]['role'][pick['role']] = {
                'pick': 0, 'role rate': 0, 'champions': []}

        r_s[pick['summoner']]['role'][pick['role']]['pick'] += 1
        r_s[pick['summoner']]['role'][pick['role']
                                      ]['champions'].append((pick['champion'], pick['result'], pick['kda'], pick['vision score'], pick['game duration']))

    for summoner in r_s:
        if r_s[summoner] != {}:
            for role in r_s[summoner]['role']:
                r_s[summoner]['role'][role]['role rate'] = "{:.2f}%".format(
                    r_s[summoner]['role'][role].get('pick', 0) / r_s[summoner]['games played'] * 100)
    return report


def merge_participants_picks_results(picks, participants, winning_team):
    d = []
    for i in range(len(picks)):
        temp = {}
        temp["champion"] = CHAMPION_IDS[str(picks[i]['champ_id'])]
        temp["role"] = picks[i]['role']
        temp["summoner"] = participants[i]['name']
        temp['kda'] = picks[i]['kda']
        temp['vision score'] = picks[i]['vision score']
        temp['game duration'] = picks[i]['game duration']

        if temp['summoner'] in winning_team:
            temp['result'] = "won"
        else:
            temp['result'] = "lost"

        d.append(temp)
    return d


def aggregate_champions_record(report):
    r_s = report['summoners']

    for s in r_s:
        for r in r_s[s]['role']:
            average_kda_per_champ = {}
            averages_per_role = {"score": 0,
                                 "games played": 0, "game duration": 0}

            champs = [(c[0], c[1]) for c in r_s[s]['role'][r]['champions']]

            champs = Counter(champs)
            temp = {}
            for c_r in champs:
                if not temp.get(c_r[0]):
                    temp[c_r[0]] = {"won": 0, "lost": 0}
                temp[c_r[0]][c_r[1]] = champs[c_r]

            for champ in temp:
                temp[champ]['win rate'] = "{:.2f}%".format(temp[champ]['won'] /
                                                           (temp[champ]['won'] + temp[champ]['lost']) * 100)

            for c in r_s[s]['role'][r]['champions']:
                averages_per_role["score"] += c[3]
                averages_per_role["games played"] += 1
                averages_per_role['game duration'] += c[4]

                k, d, a = list(map(int, c[2].split("/")))

                if not average_kda_per_champ.get(c[0]):
                    average_kda_per_champ[c[0]] = {
                        "kills": 0, "deaths": 0, "assists": 0}
                average_kda_per_champ[c[0]]['kills'] += k
                average_kda_per_champ[c[0]]['deaths'] += d
                average_kda_per_champ[c[0]]['assists'] += a
            r_s[s]['role'][r]["average vision score"] = "{:.2f}".format(
                averages_per_role['score'] / averages_per_role['games played'])

            r_s[s]['role'][r]["average game duration"] = "{:.2f}".format(
                averages_per_role['game duration'] / averages_per_role['games played'] / 60)

            r_s[s]['role'][r]['champions'] = temp

    return report


def aggregate_summoners_records(report):
    r_s = report['summoners']
    for s in r_s:
        for p in r_s[s]['partners']:
            r_s[s]['partners'][p]['win rate'] = "{:.2f}%".format(
                r_s[s]['partners'][p]['won']/(r_s[s]['partners'][p]['lost'] + r_s[s]['partners'][p]['won']) * 100)

    return report


def main():
    report = {'summoners': {}, 'champions': {
        'bans': {}, 'picks': {}, 'total games played': 0}}
    for s in SUMMONERS:
        report['summoners'][s] = {}

    match_results = SUMMONERS
    champions = CHAMPION_IDS

    for match in get_matches():
        m = Match(match)
        # updates statistics for the summoner in each game
        report = update_match_results(
            report, m.get_winning_team(), m.get_losing_team())

        # updates the ban rates of champions and such
        report = update_champions(report, m.get_all_picks(), m.get_all_bans())

        report = update_summoner_picks_and_roles(
            report, m.get_all_picks(), m.get_participants(), m.get_winning_team())

    report = aggregate_champions_record(report)
    report = aggregate_summoners_records(report)
    pp.pprint(report)


if __name__ == "__main__":
    main()
