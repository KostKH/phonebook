"""Модуль, реализующий интерфейс для операций с телефонной книгой."""
import time

from tabulate import tabulate

import settings
from domain.models import Contact
from interface import messages
from repository.repository import AbstractRepository


class UserInterruptionError(Exception):
    pass


class PhoneBook():
    """
    Класс реализует интерфейс для работы с телефонной книгой.
    Для работы нужно создать экземпляр класса, передав в него
    класс репозитория и класс модели контакта из телефонной книги.
    Для запуска интерфейса надо вызвать метод `run`.
    После этого следует следовать инструкциям, появляющимся в консоли.
    """

    def __init__(
        self,
        repository: AbstractRepository,
        contact_model: Contact
    ) -> None:
        self.repository = repository()
        self.contact_model = contact_model

    def run(self) -> None:
        """
        Метод запускает интерфейс для совершения операций с телефонной книгой.
        """
        menu_action = {
            '1': self._print_entries,
            '2': self._add_entry,
            '3': self._update_entry,
            '4': self._remove_entry,
        }
        print(messages.GREETINGS)
        while True:
            menu_choice = input(messages.CHOICE_MENU)
            time.sleep(0.5)
            if menu_choice == '0':
                print(messages.FAREWELL)
                break
            try:
                menu_action[menu_choice]()
            except KeyError:
                print(messages.INCORRECT_CHOICE)

    def _add_entry(self) -> None:
        """
        Метод реализует интерфейс для получения данных нового контакта
        и для сохранения его в репозиторий.
        """
        while True:
            input_data = {}
            fields = self.contact_model.model_fields
            keys = list(fields)
            keys.remove('uid')
            print(messages.ADD_PHONE_MSG)
            self.contact_model
            for key in keys:
                input_data[key] = input(fields[key].description + ':')
            try:
                contact_draft = self.contact_model(**input_data)
                self.repository.add(contact_draft)
                print(messages.ADD_SUCCESS)
                break
            except Exception as e:
                print(e)
                choice = input(messages.CONTINUE_OR_MAIN_MENU)
                if choice != '1':
                    break
            time.sleep(0.5)

    def _print_entries(self) -> None:
        """
        Метод реализует интерфейс для вывода на экран всех записей
        телефонной книги из репозитория.
        """
        search_string = input(messages.SEARCH_PROMPT)
        results = self.repository.get(search_string=search_string)
        self._table_print(results)

    def _update_entry(self) -> None:
        """
        Метод реализует интерфейс для выбора контакта из репозитория,
        внесения в него изменений и сохранения данных в репозиторий.
        """
        print(messages.UPDATE_INFO)
        input(messages.NEXT_SCREEN)
        search_string = input(messages.SEARCH_PROMPT)
        results = self.repository.get(search_string=search_string)
        self._table_print(results)
        try:
            contact_to_update = self._get_contact_choice(
                results,
                messages.UPDATE_CHOICE)
        except UserInterruptionError:
            return
        fields = self.contact_model.model_fields.copy()
        keys = list(fields)
        keys.remove('uid')
        print()
        for idx, key in enumerate(keys):
            print(
                f'{idx + 1}: {fields[key].description}, '
                f'текущее значение: {getattr(contact_to_update, key)}'
            )
        while True:
            try:
                field_choice = input(messages.UPDATE_FIELD_CHOICE)
                selected_keys = [keys[num - 1] for num in
                                 map(int, field_choice.rstrip().split(','))]
                break
            except (ValueError, IndexError):
                time.sleep(0.5)
                print(messages.INVALID_FIELD_INPUT)
                input(messages.CONTINUE_OR_MAIN_MENU)
        input_data = contact_to_update.model_dump().copy()
        for key in selected_keys:
            input_data[key] = input(fields[key].description + ':')
        try:
            updated_contact = self.contact_model(**input_data)
            self.repository.update(updated_contact)
            print(messages.UPDATE_SUCCESS)
        except Exception as e:
            print(e)
            print(messages.UPDATE_FAIL)

    def _remove_entry(self) -> None:
        """
        Метод реализует интерфейс для выбора контакта и удаления
        его из репозитория.
        """
        print(messages.DELETE_INFO)
        input(messages.NEXT_SCREEN)
        search_string = input(messages.SEARCH_PROMPT)
        results = self.repository.get(search_string=search_string)
        self._table_print(results)
        try:
            contact_to_delete = self._get_contact_choice(
                results,
                messages.DELETE_CHOICE)
        except UserInterruptionError:
            return
        self.repository.remove(contact_to_delete)
        print(messages.DELETE_SUCCESS)

    def _table_print(self, results) -> None:
        """
        Вспомогательный метод для вывода на экран результатов,
        полученных из репозитория. Метод выводит список контактов
        в табличном виде.
        """
        fields = self.contact_model.model_fields
        headers = ['#',]
        headers.extend(fields[key].description for key in fields.keys())
        screens = []
        tabular_results = []
        for idx, result in enumerate(results):
            line = [idx + 1,]
            line.extend(result.model_dump().values())
            tabular_results.append(line)
            if (
                (idx + 1) % settings.OUTPUT_LINE_NUMBER == 0
                or idx + 1 == len(results)
            ):
                screens.append(tabular_results.copy())
                tabular_results.clear()
        for idx, screen in enumerate(screens):
            print(tabulate(screen, headers=headers, tablefmt='outline'))
            if idx + 1 < len(screens):
                input(messages.NEXT_SCREEN)

    def _get_contact_choice(
        self,
        results: list[Contact],
        choice_message: str
    ) -> Contact:
        """
        Вспомогательный метод для получения от пользователя
        номера строки, подлежащей изменению или удалению. Возвращает
        соответствующий номеру контакт
        """
        while True:
            choice = input(choice_message)
            try:
                return results[int(choice) - 1]
            except (ValueError, IndexError):
                time.sleep(0.5)
                print(messages.INVALID_CONTACT_INPUT)
                continue_or_exit = input(messages.CONTINUE_OR_MAIN_MENU)
                if continue_or_exit != '1':
                    raise UserInterruptionError
