import json
from chat_settings import ChatSettings, NotificationSettings


DB_FILE = 'db.json'


def save(peer_id: int, settings: ChatSettings):
    with open(DB_FILE, 'r') as file:
        data = json.load(file)
    data[str(peer_id)] = settings.to_dict()
    with open(DB_FILE, 'w') as file:
        json.dump(data, file)


def get(peer_id: int) -> ChatSettings:
    with open(DB_FILE, 'r') as file:
        data = json.load(file)
    settings = data.get(str(peer_id))
    if settings:
        return ChatSettings.from_dict(settings)
    else:
        return ChatSettings(
            new_post_notifications=True,
            notification_settings=NotificationSettings([], [], [])
        )
