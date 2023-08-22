import os
from dataclasses import asdict, dataclass
from uuid import uuid4

import pytest

import settings
from domain.models import Contact


@dataclass(frozen=True)
class ContactInput():
    first_name: str = ''
    last_name: str = ''
    parent_name: str = ''
    organization: str = ''
    work_phone: str = ''
    mobile_phone: str = ''


valid_contact_data = [
    ContactInput(
        first_name='А',
        mobile_phone='+7',
    ),
    ContactInput(
        first_name='А',
        work_phone='23',
    ),
    ContactInput(
        first_name='А' * 20,
        mobile_phone='+7',
    ),
    ContactInput(
        first_name='А',
        mobile_phone='7' * 12,
    ),
    ContactInput(
        first_name='А',
        work_phone='7' * 12,
    ),
    ContactInput(
        first_name='А',
        last_name='б' * 20,
        work_phone='7' * 12,
    ),
    ContactInput(
        first_name='А',
        parent_name='б' * 20,
        work_phone='7',
    ),
    ContactInput(
        first_name='А',
        organization='б' * 50,
        work_phone='7',
    ),
    ContactInput(
        first_name='А' * 20,
        last_name='Бк' * 10,
        parent_name='Сд' * 10,
        organization='Ра' * 25,
        work_phone='7' * 5,
        mobile_phone='8' * 12,
    ),
    ContactInput(
        first_name='А',
        last_name='',
        parent_name='',
        organization='',
        work_phone='',
        mobile_phone='8' * 12,
    ),
]

invalid_contact_data = [
    ContactInput(
        mobile_phone='+7',
    ),
    ContactInput(
        first_name='А',
    ),
    ContactInput(
        first_name='А' * 21,
        mobile_phone='+7',
    ),
    ContactInput(
        first_name='А',
        mobile_phone='7' * 13,
    ),
    ContactInput(
        first_name='А',
        work_phone='7' * 13,
    ),
    ContactInput(
        first_name='А',
        last_name='б' * 21,
        work_phone='7' * 12,
    ),
    ContactInput(
        first_name='А',
        parent_name='б' * 21,
        work_phone='7',
    ),
    ContactInput(
        first_name='А',
        organization='б' * 51,
        work_phone='7',
    ),
    ContactInput(
        first_name='А' * 21,
        last_name='Бк' * 10,
        parent_name='Сд' * 10,
        organization='Ра' * 25,
        work_phone='7' * 5,
        mobile_phone='8' * 12,
    ),
    ContactInput(
        first_name='А',
        last_name='',
        parent_name='',
        organization='',
        work_phone='',
        mobile_phone='8' * 13,
    ),
]


@pytest.fixture
def test_db():
    temp_db = settings.BASE_DIR / 'test_db.csv'
    temp_db.touch()
    yield temp_db
    os.remove(temp_db)


@pytest.fixture
def contact_dict_data_with_uid():
    contacts = []
    for item in valid_contact_data:
        item_as_dict = asdict(item)
        item_as_dict['uid'] = str(uuid4())
        contacts.append(item_as_dict)
    return contacts


@pytest.fixture
def contact_list():
    return [Contact(**asdict(item)) for item in valid_contact_data]
