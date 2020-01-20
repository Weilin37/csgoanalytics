import attr
import pandas as pd
import psycopg2


connection = psycopg2.connect(user = "postgres",
                                  password = "admin",
                                  host = "localhost",
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
                        public.entities
                    where
                        player_name = '""" + name + """'"""
    
    # execute query to pandas dataframe
    def execute_query(self):
        return pd.read_sql_query(self.query, connection)