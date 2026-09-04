
# -*- coding: utf-8 -*-

import os
from api import db, db_path
from api.models import Potlucks, Subgroups, Contributions


### mock tables
Potlucks_ = [
    {
        'id': 1,
        'event_date': '2026-08-08',
        'time_begin': '17:00',
        'time_end': '20:00',
        'title': 'BBQ de l\'été',
        'organizer': 'Maman et papa',
        'location': 'Chez maman et papa'
    }
]
Subgroups_ = [
    {
        'id': 1,
        'name': 'Maman et papa',
        'potluck_id': 1
    },
    {
        'id': 2,
        'name': 'Pierre',
        'potluck_id': 1
    }
]
Contributions_ = [
    {
        'id': 1,
        'name': 'Chili végétarian',
        'category': 'Repas principal',
        'notes': 'Contient des haricots et des tomates',
        'subgroup_id': 1
    },
    {
        'id': 2,
        'name': 'Tarte aux pommes',
        'category': 'Dessert',
        'notes': 'Croute faite maison',
        'subgroup_id': 2
    }
]

### load mock tables into db
def load_mock_tables():
    for p in Potlucks_:
        db.session.add(Potlucks.from_dict(p))
    for s in Subgroups_:
        db.session.add(Subgroups.from_dict(s))
    for c in Contributions_:
        db.session.add(Contributions.from_dict(c))
    db.session.commit()

### initialize db
def init_db():
    '''
    Création de la table (si elle n'existe pas)
    '''
    dbExists = os.path.exists(db_path)
    db.create_all()
    if not dbExists:
        print("Db does not exists. Creating db...")
        load_mock_tables()

### CRUD operations
def fetch_all(model, fk_field: str = None, fk_value: int = None) -> list:
    """
    Fetches all records from a table, or filters child records by foreign key.
    Returns a list of model instances.
    """
    query = model.query
    # If foreign key parameters are provided, dynamically filter the query
    if fk_field is not None and fk_value is not None:
        query = query.filter(getattr(model, fk_field) == fk_value)
    return query.all()

def fetch_by_id(model, record_id: int):
    """
    Fetches a single record by its primary key ID from the database.
    Returns the model instance, or None if not found.
    """
    return db.session.get(model, record_id)

def create(model):
    """
    Adds a new model instance to the database, commits the transaction,
    and returns the saved model object with its populated ID.
    """
    db.session.add(model)
    db.session.commit()
    return model

def update(model, id: int, record: dict):
    item = db.session.get(model, id)
    if item is None:
        return None
    item.update(record)
    db.session.commit()
    return item

def delete(model, id: int) -> bool:
    item = db.session.get(model, id)
    if item is None:
        return False
    db.session.delete(item)
    db.session.commit()
    return True

