"""Модуль с классами для работы с постоянным хранилищем данных."""
import abc
import csv
from typing import Literal

import settings
from domain.models import Contact


class RepositoryNotUniqueError(Exception):
    pass


class RepositoryNotFoundError(Exception):
    pass


class AbstractRepository(abc.ABC):
    """Абстрактный репозиторий. Задает фреймворк и основные методы
    для работы с хранилищем данных. Конкретные реализации репозитория
    должны наследоваться от этого класса."""

    def add(self, contact: Contact) -> None:
        """Метод для добавления контакта в репозиторий."""
        self._add(contact)

    def update(self, contact: Contact) -> None:
        """Метод для обновления контакта в репозитории."""
        self._update(contact)

    def get(
        self,
        search_string: str | None = None
    ) -> list[Contact]:
        """Метод для получения контактов из репозитория."""
        return self._get(search_string)

    def remove(self, contact: Contact) -> None:
        """Метод для удаления контактов из репозитория."""
        self._remove(contact)

    @abc.abstractmethod
    def _add(self, contact: Contact) -> None:
        """Абстрактный метод для добавления контактов в репозиторий."""
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, search_string: str | None = None) -> list[Contact]:
        """Абстрактный метод для вывода списка контактов из репозитория."""
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(self, contact: Contact) -> None:
        """Абстрактный метод для удаления контакта из репозитория."""
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, contact: Contact) -> None:
        """Абстрактный метод для изменения контакта в репозитории."""
        raise NotImplementedError


class CsvRepository(AbstractRepository):
    """Класс репозитория, реализующий хранение контактов в csv-файле."""

    def __init__(self):
        super().__init__()
        self.db = settings.DB_NAME
        self._contact_fields = list(Contact.model_fields)
        self.db.touch()

    def _add(self, contact: Contact) -> None:
        """Метод для сохранения контакта в csv-файле."""
        check_uid_in_file = self._get(str(contact.uid))
        if check_uid_in_file:
            raise RepositoryNotUniqueError('UID already in database')
        with open(self.db, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(
                csv_file,
                fieldnames=self._contact_fields,
            )
            csv_writer.writerow(contact.model_dump())

    def _get(self, search_string: str = None) -> list[Contact]:
        """Метод для получения списка контактов из csv-файла."""
        results = []
        with open(self.db, 'r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(
                csv_file,
                fieldnames=self._contact_fields,
            )
            for row in csv_reader:
                if search_string and not self._get_match(search_string, row):
                    continue
                results.append(Contact(**row))
        return results

    def _update(self, contact: Contact):
        """Метод для обновления данных контакта в csv-файле."""
        self._update_delete(contact, mode='update')

    def _remove(self, contact: Contact):
        """Метод для удаления контакта из csv-файла."""
        self._update_delete(contact, mode='remove')

    def _update_delete(
        self,
        contact: Contact,
        mode: Literal['update', 'remove'] = 'update'
    ) -> None:
        """Вспомогательный метод, реализующий общую логику для
        удаления / изменения контакта в csv-файле."""
        contacts = self._get()
        try:
            contacts.remove(contact)
        except Exception:
            raise RepositoryNotFoundError
        contact_dicts = [item.model_dump()
                         for item in contacts]
        if mode != 'remove':
            contact_dicts.append(contact.model_dump())
        with open(self.db, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(
                csv_file,
                fieldnames=self._contact_fields,
            )
            csv_writer.writerows(contact_dicts)

    @staticmethod
    def _get_match(search_string: str, row: str) -> bool:
        """Вспомогательный метод, который проверяет,
        присутствует ли поисковый текст в строке ."""
        return search_string.lower() in ' '.join(row.values()).lower()
