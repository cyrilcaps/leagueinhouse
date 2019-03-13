from config import *
import requests
import pprint

from match import Match

from os import listdir, mkdir
from os.path import isfile, join, dirname, abspath
import json

pp = pprint.PrettyPrinter(indent=4)


def get_matches():
    matches = []
    matches_d = dirname(abspath(__file__)) + \
        "/match_data"

    for match in listdir(matches_d):
        with open(matches_d + "/" + match) as m:
            matches.append(json.load(m))

    return matches


def get_results(match):
    pass


def get_participant_identities(match):
    return match['participantIdentities']


def update_match_results_helper(report, status, team):
    for s in team:
        if report.get(s, None) != None:
            if report[s].get(status):
                report[s][status] += 1
            else:
                report[s][status] = 1

            if report[s].get('games played'):
                report[s]['games played'] += 1
            else:
                report[s]['games played'] = 1
        else:
            report[s] = {}
            report[s][status] = 1
            report[s]['games played'] = 1

    return report


def update_match_results(report, winners, losers):
    report = update_match_results_helper(report, "won", winners)
    report = update_match_results_helper(report, "lost", losers)
    return report


def generate_percentages(report):
    for s in report:
        if report[s].get('won'):
            report[s]['win rate'] = str(
                report[s]['won']/report[s]['games played'] * 100) + "%"
        else:
            report[s]['win rate'] = 0
    return report


if __name__ == "__main__":
    report = {}
    for s in SUMMONERS:
        report[s] = {}

    match_results = SUMMONERS
    count = 0
    for match in get_matches():
        m = Match(match)
        report = update_match_results(
            report, m.get_winning_team(), m.get_losing_team())
        count += 1

    report = generate_percentages(report)
    pp.pprint(report)
