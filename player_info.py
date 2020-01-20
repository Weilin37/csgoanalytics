import attr
import pandas as pd
import queries

@attr.s
class player:
    # Holds player data

    # Attributes:
    # name: name of the player
    # games_id: a pandas dataframe that contains the games that the player is involved in as well as their in game id
    name = attr.ib(default = attr.Factory(str))
    games_id = attr.ib(default = attr.Factory(pd.DataFrame))
    
    # populate the games_id attribute
    def populate_games_id(self):
        player_query = queries()
        player_query.entities_player_query(self.name)
        self.games_id = player_query.execute_query()