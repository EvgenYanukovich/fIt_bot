import asyncio
from typing import Tuple

from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Bot, Message, rules

import db
from chat_settings import (
    ChatSettings,
    NotificationSettings,
    Specialties,
    Courses,
    Forms,
    specialties_names,
    courses_names,
    forms_names
)


GROUP_ID = -215533989

bot = Bot(token='753b6d2af4be2474f230397314391c9b56282ee801dd1bcf8419b0952fd43ef4fe4da5f2eb05966ecd41e')

def toggle(data: list, value):
    if value in data:
        data.remove(value)
    else:
        data.append(value)

def get_keyboard(chat_settings: ChatSettings):
    colors = (KeyboardButtonColor.SECONDARY, KeyboardButtonColor.POSITIVE)
    kb = Keyboard(one_time=True)
    for member in Specialties:
        id_ = member.value
        kb.add(Text(
            specialties_names[id_],
            {'action': 'change_settings', 'field': 'specialties', 'value': id_}
        ), colors[member in chat_settings.notification_settings.specialties])
    kb.row()
    for member in Courses:
        id_ = member.value
        kb.add(Text(
            courses_names[id_],
            {'action': 'change_settings', 'field': 'courses', 'value': id_}
        ), colors[member in chat_settings.notification_settings.courses])
    kb.row()
    for member in Forms:
        id_ = member.value
        kb.add(Text(
            forms_names[id_],
            {'action': 'change_settings', 'field': 'forms', 'value': id_}
        ), colors[member in chat_settings.notification_settings.forms])
    kb.row()
    kb.add(Text(
        'Уведомлять о новых записях',
        {'action': 'change_settings', 'field': 'new_post_notifications',
         'value': not chat_settings.new_post_notifications}
    ), colors[chat_settings.new_post_notifications])
    kb.row()
    kb.add(Text('Закрыть'), KeyboardButtonColor.NEGATIVE)

    return kb.get_json()


@bot.on.message(rules.CommandRule('настройки', prefixes=['!', '/'], args_count=0))
async def settings_menu(message: Message):
    settings = db.get(message.peer_id)
    kb = get_keyboard(settings)
    await message.answer(
        message='Просмотр и изменение настроек диалога:',
        keyboard=kb,
        random_id=0
    )


@bot.on.message(rules.CommandRule('настройки', prefixes=['!', '/'], args_count=1))
async def settings_special(message: Message, args: Tuple[str]):
    action = args[0].lower()
    if action in ('сбросить',):
        settings = ChatSettings(
            new_post_notifications=False,
            notification_settings=NotificationSettings([], [], [])
        )
        text = 'Настройки успешно сброшены'
    elif action in ('все',):
        settings = ChatSettings(
            new_post_notifications=True,
            notification_settings=NotificationSettings(
                specialties=[s for s in Specialties],
                courses=[c for c in Courses],
                forms=[f for f in Forms]
            )
        )
        text = 'Все настройки были включены'
    else:
        settings = db.get(message.peer_id)
        text = 'Просмотр и изменение настроек диалога:'
    db.save(message.peer_id, settings)
    kb = get_keyboard(settings)
    await message.answer(
        message=text,
        keyboard=kb,
        random_id=0
    )


@bot.on.message(payload_map={'action': 'change_settings'})
async def change_settings(message: Message):
    settings = db.get(message.peer_id).to_dict()
    payload = message.get_payload_json()
    field, value = payload['field'], payload['value']
    if field in ('new_post_notifications',):
        settings[field] = value
    else:
        toggle(settings['notification_settings'][field], value)
    settings = ChatSettings.from_dict(settings)
    kb = get_keyboard(settings)
    db.save(message.peer_id, settings)
    await message.answer(
        message='Изменения сохранены',
        keyboard=kb,
        random_id=0
    )

if __name__ == '__main__':
    bot.run_forever()
