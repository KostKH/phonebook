"""Точка входа в приложение. Запускает интерфейс."""
from domain.models import Contact
from interface.interface import PhoneBook
from repository.repository import CsvRepository

if __name__ == '__main__':
    app = PhoneBook(repository=CsvRepository, contact_model=Contact)
    app.run()
