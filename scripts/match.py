import pprint
pp = pprint.PrettyPrinter(indent=2)
import datetime
from collections import OrderedDict
import json

import config

class Match:
    def __init__(self, match):
        self.data = match
        self.date = self.convert_epoch_to_datetime(self.data['gameCreation'])
        self.game_duration = str(
            self.data['gameDuration'] // 60) + " Minutes and " + str(
                self.data['gameDuration'] % 60) + " Seconds"
        self.set_participants(match['participantIdentities'])
        self.match_id = match['gameId']

        self.set_teams(self.participants[:5], self.participants[5:])
        self.set_match_results()

        self.blue_bans = [b['championId'] for b in match['teams'][0]['bans']]
        self.red_bans = [b['championId'] for b in match['teams'][1]['bans']]

        self.blue_team_stats = self.data['teams'][0]
        self.red_team_stats = self.data['teams'][1]
        self.max_stats = self.get_max_stats()['max']

        self.all_picks = []
        for b in match['participants']:
            self.all_picks.append({
                'champ_id':
                b['championId'],
                'role':
                b['timeline'].get('lane', 'Role not determined'),
                'participant_id':
                b['participantId'],
                "kda":
                "{}/{}/{}".format(b['stats']['kills'], b['stats']['deaths'],
                                  b['stats']['assists']),
                'vision score':
                b['stats']['visionScore'],
                "game duration":
                self.data['gameDuration'],
                "minions killed":
                b['stats']['totalMinionsKilled'],
                "jungle minions killed":
                b['stats']['neutralMinionsKilled'],
                "items": [
                    b['stats']['item0'], b['stats']['item1'],
                    b['stats']['item2'], b['stats']['item3'],
                    b['stats']['item4'], b['stats']['item5'],
                    b['stats']['item6']
                ]
            })

        self.blue_picks = self.all_picks[:5]
        self.red_picks = self.all_picks[5:]

    def get_team_stats(self):
        return ((self.blue_team_stats, self.red_team_stats))

    def get_game_duration(self):
        return self.game_duration

    def convert_epoch_to_datetime(self, e_t):
        return datetime.datetime.fromtimestamp(float(e_t) / 1000.)

    def get_date(self):
        return self.date

    def get_blue_bans(self):
        return self.blue_bans

    def get_red_bans(self):
        return self.red_bans

    def get_all_bans(self):
        return self.blue_bans + self.red_bans

    def get_blue_picks(self):
        return self.get_blue_picks

    def get_red_picks(self):
        return self.get_red_picks

    def get_all_picks(self):
        return self.all_picks

    def get_participants(self):
        return self.participants

    def set_participants(self, participants):
        self.participants = participants

    def get_teams(self):
        return {"blue": self.blue_team, "red": self.red_team}

    def set_teams(self, blue_team, red_team):
        self.blue_team = [p['name'] for p in blue_team]
        self.red_team = [p['name'] for p in red_team]

    def get_winning_team(self):
        if self.winning_team_color == "blue":
            return self.blue_team
        elif self.winning_team_color == "red":
            return self.red_team
        else:
            return ["winning team can not be determined"]

    def get_losing_team(self):
        if self.losing_team_color == "blue":
            return self.blue_team
        elif self.losing_team_color == "red":
            return self.red_team
        else:
            return ["winning team can not be determined"]

    def get_max_stats(self):
        team_stats = {"red":{},"blue":{},"total":{},"max":{}}
        for participant in self.data['participants']:
            stats = participant['stats']
            for key, value in stats.items():
                # if participant['teamId'] == 100:
                #     team_key = "red"
                # else:
                #     team_key = "blue"

                # try:
                #     team_stats[team_key][key] += value
                # except:
                #     team_stats[team_key][key] = value
                # try:
                #     team_stats['total'][key] += value
                # except:
                #     team_stats['total'][key] = value
                try:
                    if value > team_stats['max'][key]:
                        team_stats['max'][key] = value
                except:
                    team_stats['max'][key] = value
        return team_stats

    def get_performance_score(self, stats, summoner):
        score = 0
        for stat in stats:
            if stat in ['totalDamageDealtToChampions','totalDamageTaken','goldEarned',
                    'damageDealtToObjectives','damageDealtToTurrets',
                    'totalUnitsHealed','totalHeal','timeCCingOthers',
                    'totalMinionsKilled','neutralMinionsKilled', 
                    'neutralMinionsKilledTeamJungle','neutralMinionsKilledEnemyJungle',
                    'visionScore','visionWardsBoughtInGame','wardsPlaced','wardsKilled',
                    'kills','deaths','assists']:
                if stats[stat] > 0:
                    raw_score = float(summoner[stat])/float(stats[stat]) * config.STAT_MULTIPLIER[stat]
                    score += raw_score
                    # print("\t{}: {} ({}/{} * {})".format(stat, raw_score, summoner[stat], stats[stat], config.STAT_MULTIPLIER[stat]))
        return score

    def get_performance_scores(self):
        performance_scores = {}
        for i in range(len(self.data['participantIdentities'])):
            name = self.data['participantIdentities'][i]['name']
            s = self.data['participants'][i]
            # print(name)
            performance_score = self.get_performance_score(self.max_stats, s['stats'])
            # print("\t{}".format(performance_score))
            performance_scores[name] = performance_score
        return OrderedDict(sorted(performance_scores.items(), key=lambda x: x[1]))

    def get_match_ups(self):
        d = []
        for i in range(len(self.data['participantIdentities'])):
            name = self.data['participantIdentities'][i]['name']
            s = self.data['participants'][i]
            performance_score = self.get_performance_score(self.max_stats, s['stats'])
            summoner = {
                "summoner": name,
                "champ": s['championId'],
                "performance_score": performance_score,
                "assists": s['stats']['assists'],
                "kills": s['stats']['kills'],
                "deaths": s['stats']['deaths'],
                "role": s['timeline']['lane'],
                "cs": s['stats']['totalMinionsKilled'],
                "vision": s['stats']['visionScore'],
                "overall_damage": s['stats']['totalDamageDealt'],
                "total_champ_damage":
                s['stats']['totalDamageDealtToChampions'],
                "total_damage_taken": s['stats']['totalDamageTaken'],
                "vision_wards_bought": s['stats']['visionWardsBoughtInGame'],
                "sight_wards_bought": s['stats']['sightWardsBoughtInGame'],
                'win': s['stats']['win'],
                'gold_earned': s['stats']['goldEarned'],
                'wards_killed': s['stats']['wardsKilled'],
                "jungle_minions_killed": s['stats']['neutralMinionsKilled'],
                "damage_dealt_to_objectives":
                s['stats']['damageDealtToObjectives'],
                "damage_taken": s['stats']['totalDamageTaken'],
                "heal": s['stats']['totalHeal'],
                "wards_killed": s['stats']['wardsKilled'],
                "champ_level": s['stats']['champLevel'],
                "triple_kills": s['stats']['tripleKills'],
                "turret_kills": s['stats']['turretKills'],
                "unreal_kills": s['stats']['unrealKills'],
                "quadra_kills": s['stats']['quadraKills'],
                "killing_spree_streak": s['stats']['killingSprees'],
                "first_blood_assist": s['stats']['firstBloodAssist'],
                "first_blood_kill": s['stats']['firstBloodKill'],
                "timeline": s['timeline']
            }

            if (i < 5):
                summoner['items'] = [
                    s['stats']['item6'], s['stats']['item1'],
                    s['stats']['item2'], s['stats']['item3'],
                    s['stats']['item4'], s['stats']['item5'],
                    s['stats']['item0']
                ]
            else:
                summoner['items'] = [
                    s['stats']['item0'], s['stats']['item1'],
                    s['stats']['item2'], s['stats']['item6'],
                    s['stats']['item3'], s['stats']['item5'],
                    s['stats']['item4']
                ]
            d.append(summoner)

        t1 = d[:5]
        t2 = d[5:]

        for t in [t1, t2]:
            b_p = []
            for p in t:
                if p['role'] == "BOTTOM":
                    b_p.append(p)
            if b_p[0]['cs'] > b_p[1]['cs']:
                for t in d:
                    if t['summoner'] == b_p[1]['summoner']:
                        t['role'] = "SUPPORT"
            else:
                for t in d:
                    if t['summoner'] == b_p[0]['summoner']:
                        t['role'] = "SUPPORT"

        w_t = self.get_winning_team()
        c_t = self.get_teams()

        data = {
            "MIDDLE": [],
            "TOP": [],
            "SUPPORT": [],
            "BOTTOM": [],
            "JUNGLE": []
        }

        for p in d:
            if p['summoner'] in w_t:
                p['result'] = "won"
            else:
                p['result'] = "lost"
            data[p['role']].append(p)
        return data

    def set_match_results(self):
        l_t = "undetermined"
        w_t = "undetermined"
        if self.data.get('teams', [{}])[0].get('win', '') == "Win":
            w_t = "blue"
            l_t = "red"
        elif self.data.get('teams', [{}])[1].get('win', '') == "Win":
            w_t = "red"
            l_t = "blue"
        else:
            pass

        self.winning_team_color = w_t
        self.losing_team_color = l_t
