import attr

@attr.s
class filter_info:
    # Stores information for adding filters to WHERE clause of queries

    # Attributes:
    # match_id: matchID, can be change to array later
    # player: player name, can be change to array later
    match_id = attr.ib(default = attr.Factory(str))
    player = attr.ib(default = attr.Factory(str))