import attr
import pandas as pd
import psycopg2

# DEPRECATED TABLE NAMES
entities_table = "public.entities"
snapshots_table = "public.snapshots"
ticks_table = "public.ticks"

hurt_table = "resultHurt"
player_table = "resultPlayer"
shoot_table = "resultShoot"
spotted_table = "resultSpotted"

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
    # DEPRECATED
    def entities_player_query(self, name):
        self.query = """
                    SELECT
                        *
                    from
                        """ + entities_table + """
                    where
                        player_name = '""" + name + """'"""


    # build a query for getting information from public.snapshots of a particular player in a particular game
    # DEPRECATED
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
    # DEPRECATED
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






    # build a query for location data from player_table for when players are in the bombsite
    # NOTE this does not include any identifier for map or match ID, since there is only 1 demo in the database for now
    # NOTE Both these identifiers will need to added in the future
    def player_bombsite_query(self):
        self.query = """
                    SELECT
                        "Position_X",
                        "Position_Y",
                        "Position_Z"
                    FROM public."{player_table}"
                    WHERE "IsInBombZone" = true""".format(player_table=player_table)

    # build a query to take everything from player_table
    # NOTE this does not include any identifier for map or match ID, since there is only 1 demo in the database for now
    # NOTE Both these identifiers will need to added in the future
    def player_all_query(self):
        self.query = """
                    SELECT *
                    FROM public."{player_table}"
                    """.format(player_table=player_table)

    # build a query to take everything from shoot_table
    # NOTE this does not include any identifier for map or match ID, since there is only 1 demo in the database for now
    # NOTE Both these identifiers will need to added in the future
    def shoot_all_query(self):
        self.query = """
                    SELECT *
                    FROM public."{shoot_table}"
                    """.format(shoot_table=shoot_table)

    
    # execute query to pandas dataframe
    def execute_query(self):
        return pd.read_sql_query(self.query, connection)