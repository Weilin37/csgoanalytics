import attr
import pandas as pd
import psycopg2

# DEPRECATED TABLE NAMES
entities_table = "public.entities"
snapshots_table = "public.snapshots"
ticks_table = "public.ticks"

# Currently in use table names
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
    def player_bombsite_query(self, filter_obj):
        # define filter for WHERE clause
        where_filter = ''

        if len(filter_obj.match_id) > 0:
            where_filter += """AND "matchID" = '{match_id}'""".format(match_id = filter_obj.match_id)
        if len(filter_obj.player) > 0:
            where_filter += """ AND "Name" = '{player}'""".format(player = filter_obj.player)

        self.query = """
                    SELECT *
                    FROM public."{player_table}"
                    WHERE
                        "IsInBombZone" = true
                        {where_filter}""".format(player_table = player_table, where_filter = where_filter)



    # build a query for finding frame where a player is both IsInBombZone and shooting
    # NOTE this does not include any identifier for map or match ID, since there is only 1 demo in the database for now
    # NOTE Both these identifiers will need to added in the future
    def bombzone_shooting_query(self, bombsites, frame_width, filter_obj):
        # define filter for WHERE clause
        where_filter = ''

        if len(filter_obj.match_id) > 0:
            where_filter += """AND public."{player_table}"."matchID" = '{match_id}'""".format(
                player_table = player_table, match_id = filter_obj.match_id)
        if len(filter_obj.player) > 0:
            where_filter += """ AND public."{player_table}"."Name" = '{player}'""".format(
                player_table = player_table, player = filter_obj.player)

        # define the box that includes the extra frame_width around the bombsite
        site1_min_X = bombsites[0][0][0] - frame_width
        site1_max_X = bombsites[0][0][1] + frame_width
        site1_min_Y = bombsites[0][1][0] - frame_width
        site1_max_Y = bombsites[0][1][1] + frame_width

        site2_min_X = bombsites[1][0][0] - frame_width
        site2_max_X = bombsites[1][0][1] + frame_width
        site2_min_Y = bombsites[1][1][0] - frame_width
        site2_max_Y = bombsites[1][1][1] + frame_width

        self.query = """
                    SELECT
                        public."{player_table}"."Frame" AS "Frame",
                        public."{player_table}"."RoundNumber" AS "RoundNumber",
                        public."{player_table}"."CurrentTime" AS "CurrentTime",
                        public."{player_table}"."Position_X" AS "Position_X",
                        public."{player_table}"."Position_Y" AS "Position_Y",
                        public."{player_table}"."Position_Z" AS "Position_Z",
                        public."{shoot_table}"."Shooter" AS "Shooter",
                        public."{shoot_table}"."Weapon" AS "Weapon"
                    FROM
                        public."{player_table}" INNER JOIN public."{shoot_table}"
                        ON ((public."{player_table}"."Frame" = public."{shoot_table}"."Frame") AND
                            (public."{player_table}"."Name" = public."{shoot_table}"."Shooter") AND
                            (public."{player_table}"."matchID" = public."{shoot_table}"."matchID"))
                    WHERE
                        public."{shoot_table}"."Weapon" != '405' AND

                        (((public."{player_table}"."Position_X" BETWEEN {site1_min_X} AND {site1_max_X}) AND
                          (public."{player_table}"."Position_Y" BETWEEN {site1_min_Y} AND {site1_max_Y}))
                          OR
                         ((public."{player_table}"."Position_X" BETWEEN {site2_min_X} AND {site2_max_X}) AND
                          (public."{player_table}"."Position_Y" BETWEEN {site2_min_Y} AND {site2_max_Y})))
                        
                        {where_filter}

                    ORDER BY "Frame"
                    """.format(player_table = player_table, shoot_table = shoot_table,
                               site1_min_X = site1_min_X, site1_max_X = site1_max_X,
                               site1_min_Y = site1_min_Y, site1_max_Y = site1_max_Y,
                               site2_min_X = site2_min_X, site2_max_X = site2_max_X,
                               site2_min_Y = site2_min_Y, site2_max_Y = site2_max_Y,
                               where_filter = where_filter)


    # execute query to pandas dataframe
    def execute_query(self):
        return pd.read_sql_query(self.query, connection)