import attr
import numpy as np
import pandas as pd
import queries
from sklearn.cluster import KMeans

@attr.s
class bombsite_situation:
    # Detect and hold data corresponding to bombsite situations

    # Attributes:
    # map_name: name of the map to detect bombsite situations on
    # bombsite_xyz: coordinates of when IsInBombZone is true for players
    # bombsites: a numpy array that stores approximate bombsite locations for the map
    map_name = attr.ib(default = attr.Factory(str))
    bombsite_xyz = attr.ib(default = attr.Factory(pd.DataFrame))
    bombsites = attr.ib(default = attr.Factory(list))

    # player_data: data from player_table, used for finding bombsite situations
    # shoot_data: data from shoot_table, used for finding bombsite situations
    # bomb_frames: keeps frames of shoot_data that are relevant bomb situations, closest frame from player_data, and index of relevant row in player_data
    player_data = attr.ib(default = attr.Factory(pd.DataFrame))
    shoot_data = attr.ib(default = attr.Factory(pd.DataFrame))
    bomb_frames = attr.ib(default = attr.Factory(list))

    ### functions for populating bombsite situation attributes

    # populate the bombsite_xyz attribute
    def populate_bombsite_xyz(self):
        bombsite_query = queries.queries()
        bombsite_query.player_bombsite_query()
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

        # take the mean within each cluster for the approximate location of the bombsites
        bombsite1 = [np.mean(bombsite1_coord[:, 0]), np.mean(bombsite1_coord[:, 1])]
        bombsite2 = [np.mean(bombsite2_coord[:, 0]), np.mean(bombsite2_coord[:, 1])]

        # store to bombsites attribute
        self.bombsites = [bombsite1, bombsite2]

    # populate the player_data and shoot_data attributes
    def populate_player_shoot_data(self):

        # build relevant queries
        player_query = queries.queries()
        shoot_query = queries.queries()

        player_query.player_all_query()
        shoot_query.shoot_all_query()

        self.player_data = player_query.execute_query()
        self.shoot_data = shoot_query.execute_query()

    # get all frames from shoot_data that are relevant
    # a frame from shoot_data is relevant if:
    # 1. the most recent frame from player_data that comes before the shoot_data frame for the relevant player has this player IsInBombZone
    # 2. the active weapon is not 405, i.e. knife
    def find_bombsite_frames(self):

        # use this list to keep track of relevant frames
        relevant_frames = []

        # keep all available frames in player_data in an array
        frames = np.sort(np.unique(self.player_data['Frame']))

        # loop all frames that were recorded in shoot_data
        for idx in range(len(self.shoot_data)):
            row = self.shoot_data.iloc[idx]

            if str(row['Weapon']) != '405': # not using knife
                # find this player's closest previous frame from player_data
                closest_frame = np.max(frames[frames <= row['Frame']])
                player_closest_frame = self.player_data.loc[(self.player_data['Frame'] == closest_frame) &
                                                            (self.player_data['Name'] == row['Shooter'])]
                
                # check to see if player IsInBombZone
                if player_closest_frame.iloc[0]['IsInBombZone']:
                    # keep it if it is relevant
                    relevant_frames.append([row['Frame'], closest_frame, player_closest_frame.index[0]])

        self.bomb_frames = relevant_frames