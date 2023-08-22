from pathlib import Path
from random import choice

from domain.models import Contact
from repository.repository import CsvRepository


def test_repository_get(test_db, contact_dict_data_with_uid):
    with open(test_db, 'w') as tmp_file:
        for item in contact_dict_data_with_uid:
            text = ','.join(item.values()) + '\n'
            tmp_file.write(text)
    repository = CsvRepository()
    repository.db = test_db
    got_contacts = repository.get()
    for idx, contact in enumerate(got_contacts):
        assert isinstance(contact, Contact)
        assert contact.model_dump() == contact_dict_data_with_uid[idx]
        assert len(got_contacts) == len(contact_dict_data_with_uid)


def test_repository_get_with_search(
    test_db: Path,
    contact_dict_data_with_uid: list[dict]
):
    with open(test_db, 'w') as tmp_file:
        for item in contact_dict_data_with_uid:
            text = ','.join(item.values()) + '\n'
            tmp_file.write(text)
    repository = CsvRepository()
    repository.db = test_db
    chosen_contact_data = choice(contact_dict_data_with_uid)
    filtered_contacts = repository.get(chosen_contact_data['uid'])
    assert len(filtered_contacts) == 1
    assert isinstance(filtered_contacts[0], Contact)
    assert filtered_contacts[0].model_dump() == chosen_contact_data


def test_repository_add(test_db: Path, contact_list: list[Contact]):
    repository = CsvRepository()
    repository.db = test_db
    for contact in contact_list:
        repository.add(contact)
    expected_text = ''
    for contact in contact_list:
        string = ','.join(contact.model_dump().values()) + '\n'
        expected_text += string
    test_db_content = repository.db.read_text()
    assert test_db_content == expected_text


def test_repository_remove(
    test_db: Path,
    contact_dict_data_with_uid: list[dict]
):
    with open(test_db, 'w+') as tmp_file:
        for item in contact_dict_data_with_uid:
            text = ','.join(item.values()) + '\n'
            tmp_file.write(text)
        tmp_file.seek(0)
        count_lines_before_del = len(tmp_file.readlines())
    repository = CsvRepository()
    repository.db = test_db
    chosen_contact = Contact(**choice(contact_dict_data_with_uid))
    repository.remove(chosen_contact)
    contacts_after_removal = repository.get()
    with open(test_db, 'r') as tmp_file:
        count_lines_after_del = len(tmp_file.readlines())
    assert len(contacts_after_removal) == len(contact_dict_data_with_uid) - 1
    search_for_removed = [contact for contact in contacts_after_removal
                          if contact == chosen_contact]
    assert search_for_removed == []
    assert count_lines_after_del == count_lines_before_del - 1


def test_repository_update(
    test_db: Path,
    contact_dict_data_with_uid: list[dict]
):
    with open(test_db, 'w+') as tmp_file:
        for item in contact_dict_data_with_uid:
            text = ','.join(item.values()) + '\n'
            tmp_file.write(text)
        tmp_file.seek(0)
        count_lines_before_upd = len(tmp_file.readlines())
    repository = CsvRepository()
    repository.db = test_db
    chosen_contact_dict_init = choice(contact_dict_data_with_uid)
    chosen_contact_dict_updated = chosen_contact_dict_init.copy()
    chosen_contact_dict_updated['first_name'] = 'Updated_name'
    chosen_contact_dict_updated['last_name'] = 'Updated_surname'
    chosen_contact_dict_updated['parent_name'] = 'Updated_parent'
    chosen_contact_dict_updated['organization'] = 'Updated_organization'
    chosen_contact_dict_updated['work_phone'] = '999901'
    chosen_contact_dict_updated['mobile_phone'] = '+999902'
    contact_upd = Contact(**chosen_contact_dict_updated)
    repository.update(contact_upd)

    contact_after_update = repository.get(str(contact_upd.uid))[0]
    assert contact_after_update.model_dump() == chosen_contact_dict_updated
    with open(test_db, 'r') as tmp_file:
        count_lines_after_upd = len(tmp_file.readlines())
    assert count_lines_after_upd == count_lines_before_upd
