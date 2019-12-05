
import json

import matplotlib
import matplotlib.pyplot as plt

import firebase

def named_dict(identities):
    d = {}
    for identity in identities:
        d[identity['name']] = []
    return d

def find_name(participant_id, identities):
    for identity in identities:
        if participant_id == str(identity['participantId']):
            return identity['name']
    return None

def graph(title, x_label, x_graph, y_label, y_graph):
    fig = plt.figure(figsize=(12, 15))
    # plt.xlim(1, match_count)
    # plt.ylim(0, 1)
    plt.xlabel(x_label,fontsize=20)
    plt.ylabel(y_label,fontsize=20)
    plt.title(title,fontsize=20)

    for i, name in enumerate(y_graph.keys()):
        plt.plot(x_graph, y_graph[name], label=name)
    plt.legend(loc='upper right')
    plt.savefig('graphs/team_gold_diff_quinn.png')

def timeline_parser():
    with open('timeline_quinn.json','r') as infile:
        timeline = json.load(infile)

    identities = timeline['participantIdentities']

    objectives = []
    dragons = []
    buildings = []
    gold = named_dict(identities)
    team_gold = {'blue':[], 'red':[]}
    delta_gold = {'blue_delta':[]}
    exp = named_dict(identities)
    timestamps = []
    for frame in timeline['frames']:
        timestamp = frame['timestamp']/60000
        timestamps.append(timestamp)
        blue_gold = 0
        red_gold = 0
        for participant in frame['participantFrames']:
            participant_frame = frame['participantFrames'][participant]
            name = find_name(participant, identities)
            gold[name].append(participant_frame['totalGold'])
            exp[name].append(participant_frame['xp'])
            if int(participant) < 6:
                blue_gold += participant_frame['totalGold']
            else: 
                red_gold += participant_frame['totalGold']
        team_gold['blue'].append(blue_gold)
        team_gold['red'].append(red_gold)
        delta_gold['blue_delta'].append(blue_gold-red_gold)
        for event in frame['events']:
            if event['type'] == 'ELITE_MONSTER_KILL':
                if event['monsterType'] == 'DRAGON':
                    dragons.append(event)
                else:
                    objectives.append(event)
            if event['type'] == 'BUILDING_KILL':
                buildings.append(event)
    # print(json.dumps(objectives, indent=2))
    # print(json.dumps(buildings, indent=2))
    # data = {"objectives":objectives,"buildings":buildings}

    match_id = "MATCH-1"
    obj_doc = {"matchId": match_id, "dragons": dragons, "objectives": objectives}
    # firebase.set_document(match_id, "timeline.monsters", obj_doc)


    # firebase.set_document(match_id, "timeline.kills", obj_doc)
    
    gold_doc = {**gold, **team_gold, **delta_gold}
    # firebase.set_document(match_id, "timeline.gold", gold_doc)

    graph("Total Gold", "Time", timestamps, "Gold", delta_gold)

if __name__ == '__main__':
    timeline_parser()
