from typing import List
from enum import Enum
from dataclasses import dataclass


specialties_names = [
    'ПОИТ',
    'ИСиТ',
    'ДЭиВИ',
    'ПОИБМС'
]

courses_names = [
    '1 курс',
    '2 курс',
    '3 курс',
    '4 курс'
]

forms_names = [
    'Бюджет',
    'Платно'
]


class Specialties(Enum):
    POIT = 0
    ISIT = 1
    DEIVI = 2
    POIBMS = 3


class Courses(Enum):
    FIRST = 0
    SECOND = 1
    THIRD = 2
    FOURTH = 3


class Forms(Enum):
    BUDGET = 0
    PAID = 1


@dataclass()
class NotificationSettingsBase:
    specialties: List['Specialties']
    courses: List['Courses']
    forms: List['Forms']


@dataclass()
class ChatSettingsBase:
    new_post_notifications: bool
    notification_settings: 'NotificationSettings'


class NotificationSettings(NotificationSettingsBase):
    def to_dict(self) -> dict:
        return {
            'specialties': _enums_to_values(self.specialties),
            'courses': _enums_to_values(self.courses),
            'forms': _enums_to_values(self.forms)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NotificationSettings':
        return cls(
            specialties=_values_to_enums(Specialties, data['specialties']),
            courses=_values_to_enums(Courses, data['courses']),
            forms=_values_to_enums(Forms, data['forms'])
        )


class ChatSettings(ChatSettingsBase):
    def to_dict(self) -> dict:
        return {
            'new_post_notifications': self.new_post_notifications,
            'notification_settings': self.notification_settings.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            new_post_notifications=data['new_post_notifications'],
            notification_settings=NotificationSettings.from_dict(data['notification_settings'])
        )


def _enums_to_values(enum_list: List[Enum]) -> list:
    return list(map(lambda e: e.value, enum_list))


def _values_to_enums(enum: 'T', values: list) -> List['T']:
    return [member for member in enum if member.value in values]
