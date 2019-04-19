from config import *
import requests
import pprint

from match import Match
from collections import Counter

from os import listdir, mkdir
from os.path import isfile, join, dirname, abspath
import json

import sys

pp = pprint.PrettyPrinter(indent=2)


def get_matches(season):
    matches = []
    seasons = ['season_1', 'season_2']
    if season in seasons:
        matches_ds = [dirname(abspath(__file__)) + "/" + season]
    elif season == 'overall':
        matches_ds = [dirname(abspath(__file__)) + "/season_1"]
        matches_ds = matches_ds + [dirname(abspath(__file__)) + "/season_2"]
    else:
        print(
            "Invalid or no season found (please use 'season_1' or 'season_2'")
        sys.exit()

    for matches_d in matches_ds:
        for match in listdir(matches_d):
            with open(matches_d + "/" + match) as m:
                matches.append(json.load(m))

    return matches


def update_match_results_helper(report, status, team):
    r_s = report['summoners']
    for s in team:
        if not r_s.get(s):
            r_s[s] = {}
            r_s[s]['summoner'] = s
            r_s[s]['lost'] = 0
            r_s[s]['won'] = 0
            r_s[s]['games played'] = 0
            r_s[s]['win rate'] = "00.00%"

        if not r_s[s].get(status):
            r_s[s][status] = 0
        r_s[s][status] += 1

        if not r_s[s].get('games played'):
            r_s[s]['games played'] = 0
        r_s[s]['games played'] += 1

        if r_s[s].get('won', 0) > 0:
            r_s[s]['win rate'] = "{:.2f}%".format(
                r_s[s]['won'] / r_s[s]['games played'] * 100)
        else:
            r_s[s]['win rate'] = "00.00%"

    for p1 in team:
        for p2 in team:
            if p1 != p2:
                if not r_s[p1].get('partners'):
                    r_s[p1]['partners'] = {}

                if not r_s[p1]['partners'].get(p2):
                    r_s[p1]['partners'][p2] = {
                        "won": 0,
                        "lost": 0,
                        "win rate": 0
                    }

                r_s[p1]['partners'][p2][status] += 1

    return report


def update_match_results(report, winners, losers):
    report = update_match_results_helper(report, "won", winners)
    report = update_match_results_helper(report, "lost", losers)
    return report


def update_champions(report, all_picks, participants, winning_team, bans):
    r_c = report['champions']

    picks = merge_participants_picks_results(all_picks, participants,
                                             winning_team)
    picks = get_supports_from_game(picks)

    for c in r_c:
        r_c[c]['games total'] += 1

    for p in picks:
        r_c[p['champion']]['times picked'] += 1
        if p['result'] == "won":
            r_c[p['champion']]['won'] += 1
        else:
            r_c[p['champion']]['lost'] += 1
        r_c[p['champion']]['role'].add(p['role'])

    if bans:
        for b in bans:
            c = CHAMPION_IDS[str(b)]
            r_c[c]['times banned'] += 1

    return report


def get_right_roles(team):
    bottoms_index = []
    for t in range(len(team)):
        if team[t]['role'] == "BOTTOM":
            bottoms_index.append((t, team[t]['cs'], team[t]['summoner']))
    # print(bottoms_index)
    # print("returning: {}".format(sorted(bottoms_index, key=takeSecond)[0]))
    return sorted(bottoms_index, key=takeSecond)[0][0]


def get_supports_from_game(picks):
    t1 = picks[:5]
    t2 = picks[5:]

    s1 = get_right_roles(t1)
    s2 = get_right_roles(t2) + 5
    # print(picks[s1], picks[s2])
    picks[s1]['role'] = "SUPPORT"
    picks[s2]['role'] = "SUPPORT"
    return picks


def update_summoner_picks_and_roles(report, all_picks, participants,
                                    winning_team, matchups):
    picks = merge_participants_picks_results(all_picks, participants,
                                             winning_team)
    picks = get_supports_from_game(picks)

    r_s = report['summoners']
    for pick in picks:
        if not r_s[pick['summoner']].get('role'):
            r_s[pick['summoner']]['role'] = {}

        if not r_s[pick['summoner']]['role'].get(pick['role']):
            r_s[pick['summoner']]['role'][pick['role']] = {
                'pick': 0,
                'role rate': 0,
                'win rate': 0,
                'champions': []
            }

        versus = {}
        for p in matchups[pick['role']]:
            if p['summoner'] != pick['summoner']:
                versus = {
                    "champion":
                    CHAMPION_IDS[str(p['champ'])],
                    "result":
                    p['result'],
                    "score":
                    '{}/{}/{}'.format(
                        str(p['kills']), str(p['deaths']), str(p['assists'])),
                    "vision":
                    p['vision'],
                    "summoner":
                    p['summoner'],
                    "game length":
                    pick['game duration']
                }

        r_s[pick['summoner']]['role'][pick['role']]['pick'] += 1

        sum_data = {
            "summoner": pick['summoner'],
            "champion": pick['champion'],
            "result": pick['result'],
            "score": pick['kda'],
            "vision": pick['vision score'],
            "game length": pick['game duration']
        }

        r_s[pick['summoner']]['role'][pick['role']]['champions'].append(
            (sum_data, versus))

    for summoner in r_s:
        if r_s[summoner] != {}:
            for role in r_s[summoner]['role']:
                r_s[summoner]['role'][role]['role rate'] = "{:.2f}%".format(
                    r_s[summoner]['role'][role].get(
                        'pick', 0) / r_s[summoner]['games played'] * 100)
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
        temp['cs'] = picks[i]['minions killed']

        if temp['summoner'] in winning_team:
            temp['result'] = "won"
        else:
            temp['result'] = "lost"

        d.append(temp)
    return d


def aggregate_summoners_champions_record(report):
    r_s = report['summoners']

    for s in r_s:
        for r in r_s[s]['role']:
            average_kda_per_champ = {}
            averages_per_role = {
                "score": 0,
                "games played": 0,
                "game duration": 0,
            }
            match_history = {}

            p_r = [c[0] for c in r_s[s]['role'][r]['champions']]
            p_rec = [(c['champion'], c['result']) for c in p_r]

            champs = Counter(p_rec)
            temp = {}

            for c_r in champs:
                if not temp.get(c_r[0]):
                    temp[c_r[0]] = {"won": 0, "lost": 0}
                temp[c_r[0]][c_r[1]] = champs[c_r]

            for champ in temp:
                temp[champ]['win rate'] = "{:.2f}%".format(
                    temp[champ]['won'] /
                    (temp[champ]['won'] + temp[champ]['lost']) * 100)

            for c in r_s[s]['role'][r]['champions']:
                averages_per_role["score"] += c[0]['vision']
                averages_per_role["games played"] += 1
                averages_per_role['game duration'] += c[0]['game length']

                k, d, a = list(map(int, c[0]['score'].split("/")))

                if not average_kda_per_champ.get(c[0]['champion']):
                    average_kda_per_champ[c[0]['champion']] = {
                        "kills": 0,
                        "deaths": 0,
                        "assists": 0,
                        "games played": 0
                    }

                average_kda_per_champ[c[0]['champion']]['kills'] += k
                average_kda_per_champ[c[0]['champion']]['deaths'] += d
                average_kda_per_champ[c[0]['champion']]['assists'] += a
                average_kda_per_champ[c[0]['champion']]['games played'] += 1

                # print("c0")
                # pp.pprint(c[0])
                # print("c1")
                # pp.pprint(c[1])
                # print("--------------------")
                if not match_history.get(c[0]['champion']):
                    match_history[c[0]['champion']] = []
                match_history[c[0]['champion']].append((c[0], c[1]))

            a_k_p_c = average_kda_per_champ
            for c in a_k_p_c:
                a_k_p_c[c]['average kills'] = a_k_p_c[c]['kills'] / a_k_p_c[c][
                    'games played']
                a_k_p_c[c]['average assists'] = a_k_p_c[c][
                    'assists'] / a_k_p_c[c]['games played']
                a_k_p_c[c]['average deaths'] = a_k_p_c[c]['deaths'] / a_k_p_c[
                    c]['games played']

            for t in temp:
                for key in a_k_p_c[t]:
                    temp[t][key] = a_k_p_c[t][key]

                temp[t]['match history'] = match_history.get(t, [])

            r_s[s]['role'][r]["average vision score"] = "{:.2f}".format(
                averages_per_role['score'] / averages_per_role['games played'])

            r_s[s]['role'][r]["average game duration"] = "{:.2f}".format(
                averages_per_role['game duration'] /
                averages_per_role['games played'] / 60)

            r_s[s]['role'][r]['champions'] = temp

    return report


def aggregate_summoners_records(report):
    r_s = report['summoners']
    for s in r_s:
        for p in r_s[s]['partners']:
            r_s[s]['partners'][p]['win rate'] = "{:.2f}%".format(
                r_s[s]['partners'][p]['won'] /
                (r_s[s]['partners'][p]['lost'] + r_s[s]['partners'][p]['won'])
                * 100)

    return report


def aggregate_played_roles(report):
    r_s = report['summoners']

    for s in r_s:
        pref_roles = []
        pref_champs = {}
        for r in r_s[s]['role']:
            role_games = 0
            for champ in r_s[s]['role'][r]['champions']:
                games_played = r_s[s]['role'][r]['champions'][champ]['lost'] + \
                    r_s[s]['role'][r]['champions'][champ]['won']
                pref_champs[champ] = games_played
                role_games += games_played
            pref_roles.append((r, role_games))

        r_s[s]['most played roles'] = sorted(
            pref_roles, key=takeSecond, reverse=True)

        p_c = []
        for key in pref_champs:
            p_c.append((key, pref_champs[key]))
        r_s[s]['most played champs'] = sorted(
            p_c, key=takeSecond, reverse=True)

    return report


def takeSecond(elem):
    return elem[1]


def post_to_server(report, file_name):
    DEST = dirname(dirname(abspath(__file__))) + \
        "/inhouse_analyzer/overview_data"

    with open("{}/{}".format(DEST, file_name + ".json"), 'w') as outfile:
        json.dump(report, outfile)


def order_players_by_winrate(report):
    r_s = report['summoners']
    ordered_keys = []
    for s in r_s:
        ordered_keys.append(
            (s, r_s[s]['won'] / (r_s[s]['won'] + r_s[s]['lost']),
             r_s[s]['games played']))
    ordered_keys = sorted(ordered_keys, key=takeSecond, reverse=True)

    o_l = []
    n_l = []
    for x in ordered_keys:
        if x[2] < 5:
            n_l.append(x)
        else:
            o_l.append(x)
    ordered_keys = o_l + n_l

    r_s['sorted_summoners'] = [x[0] for x in ordered_keys]
    return report


def get_all_champions(report):
    for k in CHAMPION_IDS:
        report['champions'][CHAMPION_IDS[k]] = {
            "times banned": 0,
            "times picked": 0,
            "games total": 0,
            "won": 0,
            "lost": 0,
            "win rate": "00.00%",
            "ban rate": "00.00%",
            "pick rate": "00.00%",
            "role": set([])
        }
    return report


def aggregate_champions_records(report):
    r_c = report['champions']
    unused_champs = []
    for c in r_c:
        if r_c[c]['times banned'] == 0 and r_c[c]['times picked'] == 0:
            unused_champs.append(c)
        if r_c[c]['won'] > 0:
            r_c[c]['win rate'] = "{:.2f}%".format(
                r_c[c]['won'] / r_c[c]['times picked'] * 100)

        r_c[c]['pick rate'] = "{:.2f}%".format(
            r_c[c]['times picked'] / r_c[c]['games total'] * 100)
        r_c[c]['ban rate'] = "{:.2f}%".format(
            r_c[c]['times banned'] / r_c[c]['games total'] * 100)

        r_c[c]['role'] = list(r_c[c]['role'])

    for c in unused_champs:
        del r_c[c]

    r_c["champions"] = []
    for c in r_c:
        if c != "champions":
            r_c['champions'].append((c, int(float(r_c[c]['ban rate'][:-1]))))

    r_c['champions'] = sorted(r_c['champions'], key=takeSecond, reverse=True)
    r_c['champions'] = [x[0] for x in r_c['champions']]

    r_c['banned champions'] = []
    r_c['picked champions'] = []
    for c in r_c:
        if "champions" not in c:
            r_c['banned champions'].append((c, r_c[c]['times banned']))
            r_c['picked champions'].append((c, r_c[c]['times picked']))

    r_c['banned champions'] = sorted(
        r_c['banned champions'], key=takeSecond, reverse=True)
    r_c['picked champions'] = sorted(
        r_c['picked champions'], key=takeSecond, reverse=True)
    return report


def aggregate_role_records(report):
    r_s = report['summoners']
    for s in r_s:
        if s not in ['sorted_summoners']:
            for r in r_s[s]['role']:
                games_won = 0
                games_played = 0
                for champ in r_s[s]['role'][r]['champions']:
                    won = r_s[s]['role'][r]['champions'][champ]['won']
                    lost = r_s[s]['role'][r]['champions'][champ]['lost']
                    games_won += won
                    games_played += won + lost
                r_s[s]['role'][r]['won'] = games_won
                r_s[s]['role'][r]['lost'] = games_played - games_won
                r_s[s]['role'][r]['win rate'] = "{:.2f}%".format(
                    games_won / games_played * 100)
    return report


def main(season):
    report = {'summoners': {}, 'champions': {}}
    report = get_all_champions(report)
    matches = get_matches(season)
    for match in matches:
        m = Match(match)
        # updates statistics for the summoner in each game
        print(m.match_id)
        report = update_match_results(report, m.get_winning_team(),
                                      m.get_losing_team())

        report = update_summoner_picks_and_roles(report, m.get_all_picks(),
                                                 m.get_participants(),
                                                 m.get_winning_team(),
                                                 m.get_match_ups())

        # updates the ban rates of champions and such
        report = update_champions(report, m.get_all_picks(),
                                  m.get_participants(), m.get_winning_team(),
                                  m.get_all_bans())

    report = aggregate_summoners_champions_record(report)
    report = aggregate_summoners_records(report)
    report = aggregate_played_roles(report)
    report = order_players_by_winrate(report)
    report = aggregate_champions_records(report)
    report = aggregate_role_records(report)
    # post_to_server(report, season)

    print("processed {} matches for {}".format(len(matches), season))

    #pp.pprint(report['summoners']['Raphib737']['role']['BOTTOM'])


if __name__ == "__main__":
    season = sys.argv[1]
    main(season)
