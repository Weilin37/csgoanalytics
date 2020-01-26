import attr
import pandas as pd
import queries

@attr.s
class player:
    # Holds player data

    # Attributes:
    # name: name of the player
    # games_id: a pandas dataframe that contains the games that the player is involved in as well as their in game id
    # snapshots: a pandas dataframe that contains the snapshots of the current player, i.e. location, angle, HP, armor
    name = attr.ib(default = attr.Factory(str))
    games_id = attr.ib(default = attr.Factory(pd.DataFrame))
    snapshots = attr.ib(default = attr.Factory(pd.DataFrame))


    # populate the games_id attribute
    def populate_games_id(self):
        player_query = queries()
        player_query.entities_player_query(self.name)
        self.games_id = player_query.execute_query()


    # populate the snapshots attribute with all games that the player is involved in
    def populate_snapshots(self):
        snapshots_query = queries()

        for index, row in self.games_id.iterrows(): # this loop goes through all the games the player is involved in
            snapshots_query.snapshots_game_player_query(row["id"], row["player_id"])
            cur_game_snapshots = snapshots_query.execute_query()
            if index == 0:
                self.snapshots = cur_game_snapshots
            else:
                self.snapshots.append(cur_game_snapshots)