import attr
import pandas as pd
import psycopg2

entities_table = "public.entities"
snapshots_table = "public.snapshots"
ticks_table = "public.ticks"

connection = psycopg2.connect(user = "postgres",
                                  password = "goodgame",
                                  host = "demos.cdeosts5l1qu.us-east-2.rds.amazonaws.com",
                                  port = "5432",
                                  database = "postgres")


@attr.s
class queries:
    # Used for defining and executing queries

    # Attributes:
    # query: the string of the query
    query = attr.ib(default = attr.Factory(str))

    
    # build a query for getting player information from public.entities
    def entities_player_query(self, name):
        self.query = """
                    SELECT
                        *
                    from
                        """ + entities_table + """
                    where
                        player_name = '""" + name + """'"""


    # build a query for getting information from public.snapshots of a particular player in a particular game
    def snapshots_game_player_query(self, game_id, player_id):
        self.query = """
                    SELECT
                        *
                    from
                        """ + snapshots_table + """
                    where
                        id = '""" + str(game_id) + """' AND
                        player_id = '""" + str(player_id) + """'"""

    # build a query for getting information from public.ticks of a particular in a partciular game
    def ticks_game_player_query(self, game_id, player_id):
        self.query = """
                    SELECT
                        *
                    from
                        """ + ticks_table + """
                    where
                        id = '""" + str(game_id) + """' AND
                        (fire_entity = '""" + str(player_id) + """' OR
                         jump_entity = '""" + str(player_id) + """' OR
                         hurt_entity = '""" + str(player_id) + """' OR
                         flashed_entity = '""" + str(player_id) + """' OR
                         footstep_entity = '""" + str(player_id) + """' OR
                         swap_team_entity = '""" + str(player_id) + """' OR
                         kill_killer = '""" + str(player_id) + """' OR
                         kill_victim = '""" + str(player_id) + """' OR
                         kill_assister = '""" + str(player_id) + """')"""

    
    # execute query to pandas dataframe
    def execute_query(self):
        return pd.read_sql_query(self.query, connection)