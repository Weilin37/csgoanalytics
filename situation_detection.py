import attr
import numpy as np
import pandas as pd
import queries
import query_filters
from sklearn.cluster import KMeans

@attr.s
class bombsite_situation:
    # Detect and hold data corresponding to bombsite situations

    # Attributes:
    # filter_obj
    filter_obj = attr.ib(type = query_filters.filter_info)

    # map_name: name of the map to detect bombsite situations on
    # bombsite_xyz: coordinates of when IsInBombZone is true for players
    # bombsites: a numpy array that stores approximate bombsite locations for the map
    map_name = attr.ib(default = attr.Factory(str))
    bombsite_xyz = attr.ib(default = attr.Factory(pd.DataFrame))
    bombsites = attr.ib(default = attr.Factory(list))

    # bomb_frames: keeps frames of shoot_data that are relevant bomb situations, closest frame from player_data, and index of relevant row in player_data
    bomb_frames = attr.ib(default = attr.Factory(list))


    ### functions for populating bombsite situation attributes
    # populate the bombsite_xyz attribute
    def populate_bombsite_xyz(self):
        bombsite_query = queries.queries()
        bombsite_query.player_bombsite_query(self.filter_obj)

        print('populate_bombsite_xyz')
        print(bombsite_query.query)

        self.bombsite_xyz = bombsite_query.execute_query()

    # populate the bombsites attribute
    def populate_bombsites(self):

        # populate bombsite_xyz first, then get just the X and Y coordinates
        # NOTE this will need to be changed in the future when there is more than 1 demo
        self.populate_bombsite_xyz()
        xy_coord = np.float64(self.bombsite_xyz[['Position_X', 'Position_Y']])

        # find two clusters, reprenting the two bombsites
        coord_cluster = KMeans(n_clusters=2).fit(xy_coord)

        bombsite1_coord = xy_coord[coord_cluster.labels_ == 0, :]
        bombsite2_coord = xy_coord[coord_cluster.labels_ == 1, :]

        # take the min and max within each cluster for the approximate location of the bombsites
        bombsite1 = [(np.min(bombsite1_coord[:, 0]), np.max(bombsite1_coord[:, 0])),
                     (np.min(bombsite1_coord[:, 1]), np.max(bombsite1_coord[:, 1]))]
        bombsite2 = [(np.min(bombsite2_coord[:, 0]), np.max(bombsite2_coord[:, 0])),
                     (np.min(bombsite2_coord[:, 1]), np.max(bombsite2_coord[:, 1]))]

        # store to bombsites attribute
        self.bombsites = [bombsite1, bombsite2]

    # get all frames from shoot_data that are relevant
    # a frame from shoot_data is relevant if:
    # 1. the corresponding frame from player_data for the relevant player has this player IsInBombZone
    # 2. the active weapon is not 405, i.e. knife
    def find_bombsite_frames(self):

        # populate bombsite first
        self.populate_bombsites()

        # this parameter indicates how much room around the bombsite we are looking at
        frame_around_site = 100

        bomb_shoot_query = queries.queries()
        bomb_shoot_query.bombzone_shooting_query(self.bombsites, frame_around_site, 
                                                 self.filter_obj)

        print('find_bombsite_frames')
        print(bomb_shoot_query.query)
        
        self.bomb_frames = bomb_shoot_query.execute_query()