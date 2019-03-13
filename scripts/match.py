class Match:

    def __init__(self, match):
        self.data = match
        self.set_participants(match['participantIdentities'])
        self.match_id = match['gameId']

        self.set_teams(self.participants[:5], self.participants[5:])
        self.set_match_results()

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
