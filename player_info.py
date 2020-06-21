import attr
import numpy as np
import pandas as pd
import queries

@attr.s
class player:
    # Holds player data

    # Attributes:
    # name: name of the player
    # games_id: a pandas dataframe that contains the games that the player is involved in as well as their in game id
    # snapshots: a pandas dataframe that contains the snapshots of the current player, i.e. location, angle, HP, armor
    # ticks: a pandas dataframe that contains all ticks that involve the current player, i.e. shot, got shot, etc
    name = attr.ib(default = attr.Factory(str))
    games_id = attr.ib(default = attr.Factory(pd.DataFrame))
    snapshots = attr.ib(default = attr.Factory(pd.DataFrame))
    ticks = attr.ib(default = attr.Factory(pd.DataFrame))

    ### functions for populating player attributes
    # populate the games_id attribute
    def populate_games_id(self):
        player_query = queries.queries()
        player_query.entities_player_query(self.name)
        self.games_id = player_query.execute_query()


    # populate the snapshots attribute with all games that the player is involved in
    def populate_snapshots(self):
        snapshots_query = queries.queries()

        for index, row in self.games_id.iterrows(): # this loop goes through all the games the player is involved in
            snapshots_query.snapshots_game_player_query(row["id"], row["player_id"])
            cur_game_snapshots = snapshots_query.execute_query()
            if index == 0:
                self.snapshots = cur_game_snapshots
            else:
                self.snapshots.append(cur_game_snapshots)

    # populate the ticks attribute with all games that the player is involed in
    def populate_ticks(self):
        ticks_query = queries.queries()

        for index, row in self.games_id.iterrows(): # this loop goes through all the games the player is involved in
            ticks_query.ticks_game_player_query(row["id"], row["player_id"])
            cur_game_ticks = ticks_query.execute_query()
            if index == 0:
                self.ticks = cur_game_ticks
            else:
                self.ticks.append(cur_game_ticks)

    ### player statistics, only call these if the populate functions have been ran
    # propotion of times that the player was the fire_entity where the hurt_entity was non-empty
    def shoot_accuracy(self):

        per_game_accuracy = []

        for _, row in self.games_id.iterrows(): # this loop goes through all the games the player is involved in
            cur_fire_ticks = (self.ticks).loc[(self.ticks['id'].astype(str) == str(row['id'])) &
                                              (self.ticks['fire_entity'].astype(str) == str(row['player_id']))]
            miss_prop = np.mean(cur_fire_ticks['hurt_entity'] == '') # empty hurt_entity means shot missed
            per_game_accuracy.append(1 - miss_prop)
        
        return np.array(per_game_accuracy)