from dataclasses import asdict
from uuid import UUID

import pytest

from domain.models import Contact
from tests.conftest import invalid_contact_data, valid_contact_data


def test_contact_fields_are_as_expected():
    expected = [
        ('first_name', str, 'Имя'),
        ('last_name', str, 'Фамилия'),
        ('parent_name', str, 'Отчество'),
        ('organization', str, 'Организация'),
        ('work_phone', str, 'Рабочий телефон'),
        ('mobile_phone', str, 'Сотовый телефон'),
        ('uid', UUID, 'Уникальный ID'),
    ]
    model_fields = Contact.model_fields
    field_names = list(model_fields)
    field_types = [model_fields[key].annotation for key in field_names]
    field_descriptions = [model_fields[key].description for key in field_names]
    assert field_names == [field[0] for field in expected]
    assert field_types == [field[1] for field in expected]
    assert field_descriptions == [field[2] for field in expected]


@pytest.mark.parametrize('test_input', valid_contact_data)
def test_contact_is_created_with_valid_data(test_input):
    contact = Contact(**asdict(test_input))
    contact_data = contact.model_dump()
    field_names = list(Contact.model_fields)
    for name in field_names:
        if name == 'uid':
            continue
        expected_value = getattr(test_input, name)
        assert contact_data[name] == expected_value


@pytest.mark.parametrize('incorrect_input', invalid_contact_data)
def test_contact_is_not_created_with_invalid_data(incorrect_input):
    with pytest.raises(Exception):
        Contact(**asdict(incorrect_input))
