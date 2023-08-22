"""Модуль предметной области приложения. Содержит модель контакта."""
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated

CustomUid = Annotated[
    UUID,
    PlainSerializer(lambda uid: str(uid), return_type=str),
]


class Contact(BaseModel):
    """Базовая схема Контакта"""

    first_name: str = Field(
        min_length=1,
        max_length=20,
        description='Имя')
    last_name: str = Field(
        max_length=20,
        default='',
        description='Фамилия')
    parent_name: str = Field(
        max_length=20,
        default='',
        description='Отчество')
    organization: str = Field(
        max_length=50,
        default='',
        description='Организация')
    work_phone: str = Field(
        pattern=r'^[+]?\d*$',
        max_length=12,
        default='',
        description='Рабочий телефон')
    mobile_phone: str = Field(
        pattern=r'^[+]?\d*$',
        max_length=12,
        default='',
        description='Сотовый телефон')
    uid: CustomUid = Field(
        default_factory=uuid4,
        frozen=True,
        description='Уникальный ID')

    @model_validator(mode='after')
    def check_at_least_one_phone(self) -> 'Contact':
        if not self.work_phone and not self.mobile_phone:
            raise ValueError('Не введено ни одного номера телефона')
        return self

    def __eq__(self, other):
        if not isinstance(other, Contact):
            return False
        return other.uid == self.uid

    def __hash__(self):
        return hash(self.uid)
