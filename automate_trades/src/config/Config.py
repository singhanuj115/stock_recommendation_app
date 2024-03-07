import json
import os


def get_server_config():
    with open(os.path.abspath('config/server.json'), 'r') as server:
        json_server_data = json.load(server)
        return json_server_data


def get_system_config():
    with open(os.path.abspath('config/system.json'), 'r') as system:
        json_system_data = json.load(system)
        return json_system_data


def get_broker_app_config():
    with open(os.path.abspath('config/broker_app.json'), 'r') as broker_app:
        json_user_data = json.load(broker_app)
        return json_user_data


def get_holidays():
    with open(os.path.abspath('config/holidays.json'), 'r') as holidays:
        holidays_data = json.load(holidays)
        return holidays_data


def get_timestamps_data():
    server_config = get_server_config()
    timestamps_file_path = os.path.join(
        server_config['deployDir'], 'timestamps.json')
    if not os.path.exists(timestamps_file_path):
        return {}
    timestamps_file = open(timestamps_file_path, 'r')
    timestamps = json.loads(timestamps_file.read())
    return timestamps


def save_timestamps_data(timestamps=None):
    if timestamps is None:
        timestamps = {}
    server_config = get_server_config()
    timestamps_file_path = os.path.join(
        server_config['deployDir'], 'timestamps.json')
    with open(timestamps_file_path, 'w') as timestampsFile:
        json.dump(timestamps, timestampsFile, indent=2)
    print("saved timestamps data to file " + timestamps_file_path)
