import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

connection = psycopg2.connect(user = "postgres",
                                  password = "admin",
                                  host = "localhost",
                                  port = "5432",
                                  database = "postgres")

# create sqlalchemy engine
engine = create_engine("postgresql+psycopg2://postgres:admin@localhost/postgres")


def close_connection(connection, cursor):
    if (connection):
        cursor.close()
        connection.close()


##### CREATE SQL GENERATING FUNCTIONS #####
def create_demo_id(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT count(distinct id) from public.headers")
    id = str(cursor.fetchone()[0] + 1)
    print("Created a new ID: " + id)

    return id


# Insert header table
def insert_to_header(json, id, connection):
    print("Attempting to insert header data for ID: " + id)
    cursor = connection.cursor()
    data = json['header']
    map = data['map']
    tickrate = data['tickRate']
    snapshotrate = data['snapshotRate']

    dictionary = {"id": [id], "map": [map], "tickrate": [tickrate], "snapshotrate": [snapshotrate]}
    print(dictionary)
    df = pd.DataFrame(dictionary)
    df.to_sql('headers', schema='public', index=False, con=engine, if_exists='append')

    cursor.execute("SELECT count(*) FROM public.headers WHERE id='" + id + "'")
    num_records_generated = str(cursor.fetchone()[0])
    print("Inserted " + num_records_generated + " records for ID: " + id)


# Insert entities table
def insert_to_entities(json, id, connection):
    print("Attempting to insert entities data for ID: " + id)
    cursor = connection.cursor()
    ids = []
    player_ids = []
    player_names = []
    team_ids = []

    data = json['entities']
    for row in data:
        ids.append(id)
        player_ids.append(row['id'])
        player_names.append(row['name'])
        team_ids.append(row['team'])

    dictionary = {"id": ids,
                  "player_id": player_ids,
                  "player_name": player_names,
                  "team_id": team_ids}
    df = pd.DataFrame(dictionary)
    df.to_sql('entities', schema='public', index=False, con=engine, if_exists='append')

    cursor.execute("SELECT count(*) FROM public.entities WHERE id='" + id + "'")
    num_records_generated = str(cursor.fetchone()[0])
    print("Inserted " + num_records_generated + " records for ID: " + id)


# Insert snapshots table
def insert_to_snapshots(json, id, connection):
    print("Attempting to insert snapshots data for ID: " + id)
    cursor = connection.cursor()
    ids = []
    ticks = []
    player_ids = []
    position_x = []
    position_y = []
    position_z = []
    angle = []
    hp = []
    armor = []

    data = json['snapshots']
    for snapshot in data:
        currentTick = snapshot['tick']
        for row in snapshot['entityUpdates']:
            keys = row.keys()
            ids.append(id)
            ticks.append(currentTick)
            player_ids.append(row['entityId'])
            position_x.append(row['positions'][0]['x'])
            position_y.append(row['positions'][0]['y'])
            position_z.append(row['positions'][0]['z'])
            angle.append(row['angle']) if "angle" in keys else angle.append(0)
            hp.append(row['hp'])
            armor.append(row['armor']) if "armor" in keys else armor.append(0)

    print("Length of ids: " + str(len(ids)))
    print("Length of ticks: " + str(len(ticks)))
    print("Length of player_ids: " + str(len(player_ids)))
    print("Length of position_x: " + str(len(position_x)))
    print("Length of position_y: " + str(len(position_y)))
    print("Length of position_z: " + str(len(position_z)))
    print("Length of angle: " + str(len(angle)))
    print("Length of hp: " + str(len(hp)))
    print("Length of hp: " + str(len(hp)))

    dictionary = {"id": ids,
                  "tick": ticks,
                  "player_id": player_ids,
                  "position_x": position_x,
                  "position_y": position_y,
                  "position_z": position_z,
                  "angle": angle,
                  "hp": hp,
                  "armor": armor}

    df = pd.DataFrame(dictionary)
    df.to_sql('snapshots', schema='public', index=False, con=engine, if_exists='append')

    cursor.execute("SELECT count(*) FROM public.snapshots WHERE id='" + id + "'")
    num_records_generated = str(cursor.fetchone()[0])
    print("Inserted " + num_records_generated + " records for ID: " + id)


# Insert tick table
def insert_to_ticks(json, id, connection):
    print("Attempting to insert ticks data for ID: " + id)
    cursor = connection.cursor()
    ids = []
    ticks = []
    fire_entity = []
    hurt_entity = []
    flashed_entity = []
    kill_killer = []
    kill_weapon = []
    kill_victim = []
    kill_assister = []
    jump_entity = []
    footstep_entity = []
    swap_team_entity = []
    round_started = []
    round_ended_winner = []
    round_ended_reason = []

    data = json['ticks']
    for tick in data:
        currentTick = tick['nr']
        events = {}
        for event in tick['events']:
            if "name" not in event.keys():
                continue
            if event['name'] == "kill":
                for action in event['attrs']:
                    events[action['key']] = action['numVal']
            elif event['name'] == "round_started":
                events[event['name']] = 1
            elif event['name'] == "round_ended":
                for action in event['attrs']:
                    events[action['key']] = action['numVal']
            elif event['name'] in ['chat_message', 'disconnect']:
                continue
            else:
                events[event['name']] = event['attrs'][0]['numVal']

        keys = events.keys()
        ids.append(id)
        ticks.append(currentTick)

        fire_entity.append(events['fire']) if "fire" in keys else fire_entity.append('')
        jump_entity.append(events['jump']) if "jump" in keys else jump_entity.append('')
        hurt_entity.append(events['hurt']) if "hurt" in keys else hurt_entity.append('')
        flashed_entity.append(events['flashed']) if "flashed" in keys else flashed_entity.append('')
        footstep_entity.append(events['footstep']) if "footstep" in keys else footstep_entity.append('')
        swap_team_entity.append(events['swap_team']) if "swap_team" in keys else swap_team_entity.append('')
        kill_killer.append(events['killer']) if "killer" in keys else kill_killer.append('')
        kill_victim.append(events['victim']) if "victim" in keys else kill_victim.append('')
        kill_weapon.append(events['weapon']) if "weapon" in keys else kill_weapon.append('')
        kill_assister.append(events['assister']) if "assister" in keys else kill_assister.append('')
        round_ended_winner.append(events['winner']) if "winner" in keys else round_ended_winner.append('')
        round_ended_reason.append(events['reason']) if "reason" in keys else round_ended_reason.append('')
        round_started.append(events['round_started']) if "round_started" in keys else round_started.append('')

    dictionary = {"id": ids,
                  "tick": ticks,
                  "fire_entity": fire_entity,
                  "jump_entity": jump_entity,
                  "hurt_entity": hurt_entity,
                  "flashed_entity": flashed_entity,
                  "footstep_entity": footstep_entity,
                  "swap_team_entity": swap_team_entity,
                  "kill_killer": kill_killer,
                  "kill_victim": kill_victim,
                  "kill_weapon": kill_weapon,
                  "kill_assister": kill_assister,
                  "round_started": round_started,
                  "round_ended_winner": round_ended_winner,
                  "round_ended_reason": round_ended_reason}

    df = pd.DataFrame(dictionary)
    df.to_sql('ticks', schema='public', index=False, con=engine, if_exists='append')

    cursor.execute("SELECT count(*) FROM public.snapshots WHERE id='" + id + "'")
    num_records_generated = str(cursor.fetchone()[0])
    print("Inserted " + num_records_generated + " records for ID: " + id)

# Create ID
id = create_demo_id(connection)

# Load json
with open("json/demo.json", "r") as read_file:
    data = json.load(read_file)

