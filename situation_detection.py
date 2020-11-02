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

    # bomb_events: array of tuples, where first element is dataframe containing frames that are the 5 seconds that precede a bombsite event,
    # the second element is the frames during the actual bomb event
    bomb_events = attr.ib(default = attr.Factory(list))


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

        # find two clusters, representing the two bombsites
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

    # get separate bombsite events as well as corresponding preceding 5 seconds of frames
    def get_bombsite_events(self):

        # group bomb_frames by round number
        sep_by_round = self.bomb_frames.groupby(['RoundNumber'])

        # dictionary to store the grouped dataframes separately
        sep_rounds_dict = {}

        # loop through each group
        for i, grp in sep_by_round:
            # find time difference between shooting frames within this round in units of 10 seconds (1280 frames at 128 ticks)
            # each chunk of shooting frames that are separated by more than 20 seconds are considered one bombsite event
            # use cumsum to tag each frame with a relevant event_id defined within each round
            event_id = (~grp['Frame'].diff().div(1280, fill_value=0).lt(2)).cumsum()

            # make copy of grp to not get slice assignment warning from pandas
            rd_df = grp.copy(deep=True)
            # add new event_id column
            rd_df['event_id'] = event_id

            # save rd_df into dictionary
            sep_rounds_dict['df_' + str(i)] = rd_df

        # declare new empty dataframes to hold the first and last frames of the events
        event_first_frames = pd.DataFrame()
        event_last_frames = pd.DataFrame()

        # Group the dataframes by event id and get the first row (the starting frame of the event)
        for rd in sep_rounds_dict.keys():
            sep_by_event = sep_rounds_dict[rd].groupby('event_id')
            event_first_frames = event_first_frames.append(sep_by_event.first())
            event_last_frames = event_last_frames.append(sep_by_event.last())

        # reset index on both
        event_first_frames.reset_index(drop=True, inplace=True)
        event_last_frames.reset_index(drop=True, inplace=True)

        # array to store both dataframe for frames that precede event as well as frames during event
        list_event_dataframes = []

        # make queries object that will be used in the loop
        frames_query = queries.queries()

        # loop through event_first_frames and event_last_frames to get relevant frames for each event
        for ev_num in range(len(event_first_frames)):
            # Start and end frame
            start_frame = event_first_frames.iloc[ev_num]['Frame']
            end_frame = event_last_frames.iloc[ev_num]['Frame']

            # query for frames preceding event
            frames_query.player_frame_range_query(start_frame - 128 * 5, start_frame, self.filter_obj)
            preceding_frames = frames_query.execute_query()

            # query for frames during the event
            frames_query.player_frame_range_query(start_frame, end_frame + 1, self.filter_obj)
            event_frames = frames_query.execute_query()

            # Append results
            list_event_dataframes.append((preceding_frames, event_frames))

        self.bomb_events = list_event_dataframes