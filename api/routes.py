
# general modules
from flask import jsonify, request
from datetime import datetime
from werkzeug.exceptions import BadRequest, MethodNotAllowed
import unicodedata

# api modules
from api import app
from api.dao import fetch_all, fetch_by_id, create, update, delete
from api.models import Potlucks, Subgroups, Contributions


### VALIDATORS ###

def clean_string(text: str, size: int) -> str:
    # Remove category 'Cc' (Control) and 'Cf' (Format, including RTL/LTR overrides)
    cleaned = "".join(
        char for char in text
        if unicodedata.category(char) not in ("Cc", "Cf")
    )
    # Normalize whitespace (strips tabs/newlines/extra spaces)
    return " ".join(cleaned.split())[:size]

def validate_fk(model, fk: int) -> bool:
    if not fetch_by_id(model, fk):
        return False
    return True

def validate_potluck(record: dict) -> bool:
    # Format validation for dict
    if not isinstance(record, dict):
        return False
    # Format validation for key/value data type, and blank values
    schema = {
        'event_date': str,
        'time_begin': str,
        'time_end': str,
        'title': str,
        'organizer': str,
        'location': str
    }
    for field, expected_type in schema.items():
        value = record.get(field)
        if not isinstance(value, expected_type):
            return False
    record['title'] = clean_string(record['title'], 100)
    record['organizer'] = clean_string(record['organizer'], 100)
    record['location'] = clean_string(record['location'], 100)
    if not record.get('event_date'):
        return False
    if not record.get('time_begin'):
        return False
    if not record.get('title'):
        return False
    if not record.get('organizer'):
        return False
    if not record.get('location'):
        return False
    # Format validation for date (YYYY-MM-DD)
    try:
        datetime.strptime(record['event_date'], '%Y-%m-%d')
    except ValueError:
        return False
    # Format validation for time (HH:MM in 24h format)
    try:
        datetime.strptime(record['time_begin'], '%H:%M')
    except ValueError:
        return False
    try:
        datetime.strptime(record['time_end'], '%H:%M')
    except ValueError:
        return False
    if datetime.strptime(record['time_begin'], '%H:%M').time() > datetime.strptime(record['time_end'], '%H:%M').time():
        return False
    return True

def validate_subgroup(record: dict) -> bool:
    # Format validation for dict
    if not isinstance(record, dict):
        return False
    # Format validation for key/value data type, and blank values
    schema = {
        'name': str,
        'potluck_id': int
    }
    for field, expected_type in schema.items():
        value = record.get(field)
        if not isinstance(value, expected_type):
            return False
    record['name'] = clean_string(record['name'], 100)
    for field in schema:
        value = record.get(field)
        if not value:
            return False
    # Format validation for FK
    if not validate_fk(Potlucks, record.get('potluck_id')):
        return False
    return True

def validate_contribution(record: dict) -> bool:
    # Format validation for dict
    if not isinstance(record, dict):
        print("error for dict")
        return False
    # Format validation for key/value data type, and blank values
    schema = {
        'name': str,
        'category': str,
        'notes': str,
        'subgroup_id': int
    }
    for field, expected_type in schema.items():
        value = record.get(field)
        if not isinstance(value, expected_type):
            return False
    record['name'] = clean_string(record['name'], 100)
    record['category'] = clean_string(record['category'], 50)
    record['notes'] = clean_string(record['notes'], 300)
    if not record.get('name'):
        return False
    if not record.get('subgroup_id'):
        return False
    # Format validation for FK
    if not validate_fk(Subgroups, record.get('subgroup_id')):
        print("error for fk")
        return False
    return True


### ROUTES ###

# base documentation route

@app.route('/')
@app.route('/index')
def index():
    return "swagger"

def index_OLD():
    return '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Potluck Manager Server-side API</title>
    <style>
        * { margin: 0; }
        body { padding: 10px; padding-bottom: 200px; }
        h1 { margin: 20px 0 0; }
        h2 { margin: 10px 0 30px; }
        h3 { margin: 30px 0 10px; }
        ul { margin-left: 0; margin-bottom: 10px; }
    </style>
  </head>
  <body>
    <h1>Potluck Manager</h1>
    <h2>Server-side API Documentation</h2>
    <hr>
    
    <h3>Resources available :</h3>
    <ul>
        <li>/potlucks</li>
        <li>/subgroups</li>
        <li>/contributions</li>
    </ul>
    
    <h3>HTTP methods available ==> [endpoints] :</h3>
    <ul>
        <li>Create: POST ==> /[resource]</li>
        <li>Read: GET all ==> /[resource]</li>
        <li>Read: GET one ==> /[resource]/[id:int]</li>
        <li>Update: PUT ==> /[resource]/[id:int]</li>
        <li>Delete: DELETE ==> /[resource]/[id:int]</li>
    </ul>
    
    <h3>HTTP payload format :</h3>
    <ul>
        <li>JSON</li>
    </ul>
    
    <h3>HTTP response codes :</h3>
    <ul>
        <li>200 = Read/Updated. Return = affected record(s)</li>
        <li>201 = Created. Return = affected record, with auto-generated id</li>
        <li>204 = Success. Return = no content</li>
        <li>400 = Bad request. Return = error message</li>
        <li>404 = Resource not found. Return = error message</li>
    </ul>
    
    <h3>Database constraints :</h3>
    <ul>
        <li>Potluck</li>
        <ul>
            <li>id = INT, AUTOINCREMENT, PRIMARY KEY</li>
            <li>event_date = DATE, NOT NULL</li>
            <li>time_begin = TIME, NOT NULL</li>
            <li>time_end = TIME, nullable</li>
            <li>title = VARCHAR(100), NOT NULL</li>
            <li>location = VARCHAR(100), NOT NULL</li>
            <li>organizer = VARCHAR(100), NOT NULL</li>
        </ul>
        <li>Subgroups</li>
        <ul>
            <li>id = INT, AUTOINCREMENT, PRIMARY KEY</li>
            <li>name = VARCHAR(100), NOT NULL</li>
            <li>potluck_id = INT, NOT NULL, REFERENCES Potlucks(id), ON DELETE CASCADE</li>
        </ul>
        <li>Contributions</li>
        <ul>
            <li>id = INT, AUTOINCREMENT, PRIMARY KEY</li>
            <li>name = VARCHAR(100), NOT NULL</li>
            <li>category = VARCHAR(50), nullable</li>
	        <li>notes = VARCHAR(300), nullable</li>
	        <li>subgroup_id = INT, NOT NULL, REFERENCES Subgroups(id), ON DELETE CASCADE</li>
        </ul>
    </ul>
  </body>
</html>
'''


# resource routes

@app.route('/potlucks', methods=['GET'])
def get_all_potlucks():
    """
    Lister tous les potlucks
    ---
    responses:
        200:
            description: Liste des potlucks
        404:
            description: Aucun enregistrement trouvé
    """
    item = fetch_all(Potlucks)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    list = [i.to_dict() for i in item]
    return jsonify(list), 200  # 200 = updated

@app.route('/potlucks/<int:id>', methods=['GET'])
def get_one_potluck(id):
    """
    Lister un potluck avec l'identifiant
    ---
    parameters:
      - in: path
        name: potluck_id
        type: integer
        required: true
        description: L'identifiant du potluck
    responses:
        200:
            description: Liste du potluck correspondant à l'identifiant
        404:
            description: Aucun enregistrement trouvé
    """
    item = fetch_by_id(Potlucks, id)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(item.to_dict()), 200  # 200 = updated

@app.route('/potlucks/<int:id>/subgroups', methods=['GET'])
def get_potluck_all_subgroups(id):
    """
    Lister tous les subgroups associés à un potluck
    ---
    parameters:
      - in: path
        name: potluck_id
        type: integer
        required: true
        description: L'identifiant du potluck
    responses:
        200:
            description: Liste de tous les subgroups associés au potluck_id
        404:
            description: Aucun enregistrement trouvé
    """
    if not fetch_by_id(Potlucks, id):
        return jsonify({'error': 'Resource not found'}), 404
    item = fetch_all(Subgroups, fk_field="potluck_id", fk_value=id)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify([i.to_dict() for i in item]), 200  # 200 = updated

@app.route('/potlucks', methods=['POST'])
def add_potluck():
    """
    Créer un nouveau potluck
    ---
    parameters:
      - in: body
        name: payload
        description: Les informations concernant le nouveau potluck
        schema:
            type: object
            required:
                - event_date
                - time_begin
                - title
                - organizer
                - location
            properties:
                event_date:
                    type: string
                    example: "2026-01-01"
                time_begin:
                    type: string
                    example: "15:00"
                time_end:
                    type: string
                    example: "15:00"
                title:
                    type: string
                    example: "BBQ de l'été"
                organizer:
                    type: string
                    example: "Maman et papa"
                location:
                    type: string
                    example: "Chez maman et papa"
    responses:
        201:
            description: Nouveau potluck ajouté
        400:
            description: Mauvaise requête (payload invalide)
    """
    record = request.get_json()
    if not validate_potluck(record):
        return jsonify({'error': 'Bad request'}), 400
    record_obj = Potlucks.from_dict(record)
    new_record = create(record_obj)
    return jsonify(new_record.to_dict()), 201  # 201 = Created

@app.route('/potlucks/<int:id>', methods=['PUT'])
def update_potluck(id):
    """
    Modifier un potluck existant
    ---
    parameters:
      - in: path
        name: potluck_id
        type: integer
        required: true
        description: L'identifiant du potluck
      - in: body
        name: payload
        description: Les informations concernant le potluck à modifier
        schema:
            type: object
            required:
                - event_date
                - time_begin
                - title
                - organizer
                - location
            properties:
                event_date:
                    type: string
                    example: "2026-01-01"
                time_begin:
                    type: string
                    example: "15:00"
                time_end:
                    type: string
                    example: "15:00"
                title:
                    type: string
                    example: "BBQ de l'été"
                organizer:
                    type: string
                    example: "Maman et papa"
                location:
                    type: string
                    example: "Chez maman et papa"
    responses:
        200:
            description: Potluck modifié
        400:
            description: Mauvaise requête (payload invalide)
        """
    record = request.get_json()
    if not validate_potluck(record):
        return jsonify({'error': 'Bad request'}), 400
    returned_record = update(Potlucks, id, record)
    if not returned_record:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify(returned_record.to_dict()), 200  # 200 = updated

@app.route('/potlucks/<int:id>', methods=['DELETE'])
def remove_potluck(id):
    """
    Supprimer un potluck
    Attention: La suppression d'un potluck supprime automatiquement tous les subgroups et contributions associés. (DELETE ON CASCADE)
    ---
    parameters:
      - in: path
        name: potluck_id
        type: integer
        required: true
        description: L'identifiant du potluck
    responses:
        200:
            description: potluck supprimé
        404:
            description: Aucun enregistrement trouvé
    """
    if not delete(Potlucks, id):
        return jsonify({'error': 'Resource not found'}), 404
    return '', 204  # 204 = Succeeded, no content


@app.route('/subgroups', methods=['GET'])
def get_all_subgroups():
    """
    Lister tous les subgroups
    ---
    responses:
        200:
            description: Liste des subgroups
        404:
            description: Aucun enregistrement trouvé
    """
    item = fetch_all(Subgroups)
    return jsonify([i.to_dict() for i in item]), 200

@app.route('/subgroups/<int:id>', methods=['GET'])
def get_one_subgroup(id):
    """
    Lister un subgroup avec l'identifiant
    ---
    parameters:
      - in: path
        name: subgroup_id
        type: integer
        required: true
        description: L'identifiant du subgroup
    responses:
        200:
            description: Liste du subgroup correspondant à l'identifiant
        404:
            description: Aucun enregistrement trouvé
    """
    item = fetch_by_id(Subgroups, id)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(item.to_dict()), 200

@app.route('/subgroups/<int:id>/contributions', methods=['GET'])
def get_subgroup_all_contributions(id):
    """
    Lister toutes les contributions associées à un subgroup
    ---
    parameters:
      - in: path
        name: subgroup_id
        type: integer
        required: true
        description: L'identifiant du subgroup
    responses:
        200:
            description: Liste de toutes les contributions associées à 1 subgroup
        404:
            description: Aucun enregistrement trouvé
    """
    if not fetch_by_id(Subgroups, id):
        return jsonify({'error': 'Resource not found'}), 404
    item = fetch_all(Contributions, fk_field="subgroup_id", fk_value=id)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify([i.to_dict() for i in item]), 200

@app.route('/subgroups', methods=['POST'])
def add_subgroup():
    """
    Créer un nouveau subgroup
    ---
    parameters:
      - in: body
        name: payload
        description: Les informations concernant le nouveau subgroup
        schema:
            type: object
            required:
                - name
                - potluck_id
            properties:
                name:
                    type: string
                    example: "Maman et papa"
                potluck_id:
                    type: integer
                    example: "1"
    responses:
        201:
            description: Nouveau subgroup ajouté
        400:
            description: Mauvaise requête (payload invalide)
    """
    record = request.get_json()
    if not validate_subgroup(record):
        return jsonify({'error': 'Bad request'}), 400
    record_obj = Subgroups.from_dict(record)
    new_record = create(record_obj)
    return jsonify(new_record.to_dict()), 201  # 201 = Created

@app.route('/subgroups/<int:id>', methods=['PUT'])
def update_subgroup(id):
    """
    Modifier un subgroup existant
    ---
    parameters:
      - in: path
        name: subgroup_id
        type: integer
        required: true
        description: L'identifiant du subgroup
      - in: body
        name: payload
        description: Les informations concernant le subgroup à modifier
        schema:
            type: object
            required:
                - name
                - potluck_id
            properties:
                name:
                    type: string
                    example: "Maman et papa"
                potluck_id:
                    type: integer
                    example: "1"
    responses:
        200:
            description: Potluck modifié
        400:
            description: Mauvaise requête (payload invalide)
        """
    record = request.get_json()
    if not validate_subgroup(record):
        return jsonify({'error': 'Bad request'}), 400
    returned_record = update(Subgroups, id, record)
    if not returned_record:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify(returned_record.to_dict()), 200  # 200 = updated

@app.route('/subgroups/<int:id>', methods=['DELETE'])
def remove_subgroup(id):
    """
    Supprimer un subgroup
    Attention: La suppression d'un subgroup supprime automatiquement toutes les contributions associées. (DELETE ON CASCADE)
    ---
    parameters:
      - in: path
        name: subgroup_id
        type: integer
        required: true
        description: L'identifiant du subgroup
    responses:
        200:
            description: subgroup supprimé
        404:
            description: Aucun enregistrement trouvé
    """
    if not delete(Subgroups, id):
        return jsonify({'error': 'Resource not found'}), 404
    return '', 204  # 204 = Succeeded, no content


@app.route('/contributions', methods=['GET'])
def get_all_contributions():
    """
    Lister toutes les contributions
    ---
    responses:
        200:
            description: Liste des contributions
        404:
            description: Aucun enregistrement trouvé
    """
    item = fetch_all(Contributions)
    return jsonify([i.to_dict() for i in item]), 200

@app.route('/contributions/<int:id>', methods=['GET'])
def get_one_contribution(id):
    """
    Lister une contribution avec l'identifiant
    ---
    parameters:
      - in: path
        name: contribution_id
        type: integer
        required: true
        description: L'identifiant de la contribution
    responses:
        200:
            description: Liste de la contribution correspondant à l'identifiant
        404:
            description: Aucun enregistrement trouvé
    """
    item = fetch_by_id(Contributions, id)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(item.to_dict()), 200

@app.route('/contributions', methods=['POST'])
def add_contribution():
    """
    Créer une nouvelle contribution
    ---
    parameters:
      - in: body
        name: payload
        description: Les informations concernant la nouvelle contribution
        schema:
            type: object
            required:
                - name
                - subgroup_id
            properties:
                name:
                    type: string
                    example: "Chili végétarien"
                category:
                    type: string
                    example: "Repas principal"
                notes:
                    type: string
                    example: "Aucun produit d'origine animale"
                subgroup_id:
                    type: integer
                    example: "1"
    responses:
        201:
            description: Nouvelle contribution ajoutée
        400:
            description: Mauvaise requête (payload invalide)
    """
    record = request.get_json()
    print(record)
    if not validate_contribution(record):
        return jsonify({'error': 'Bad request'}), 400
    record_obj = Contributions.from_dict(record)
    new_record = create(record_obj)
    return jsonify(new_record.to_dict()), 201  # 201 = Created

@app.route('/contributions/<int:id>', methods=['PUT'])
def update_contribution(id):
    """
    Modifier une contribution existante
    ---
    parameters:
      - in: body
        name: payload
        description: Les informations concernant la contribution à modifier
        schema:
            type: object
            required:
                - name
                - subgroup_id
            properties:
                name:
                    type: string
                    example: "Chili végétarien"
                category:
                    type: string
                    example: "Repas principal"
                notes:
                    type: string
                    example: "Aucun produit d'origine animale"
                subgroup_id:
                    type: integer
                    example: "1"
    responses:
        200:
            description: Contribution modifiée
        400:
            description: Mauvaise requête (payload invalide)
        """
    record = request.get_json()
    if not validate_contribution(record):
        return jsonify({'error': 'Bad request'}), 400
    returned_record = update(Contributions, id, record)
    if not returned_record:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify(returned_record.to_dict()), 200  # 200 = updated

@app.route('/contributions/<int:id>', methods=['DELETE'])
def remove_contribution(id):
    """
    Supprimer une contribution
    ---
    parameters:
      - in: path
        name: contribution_id
        type: integer
        required: true
        description: L'identifiant du contribution
    responses:
        200:
            description: contribution supprimée
        404:
            description: Aucun enregistrement trouvé
    """
    if not delete(Contributions, id):
        return jsonify({'error': 'Resource not found'}), 404
    return '', 204  # 204 = Succeeded, no content


# error handlers

@app.errorhandler(404)
def not_found_404(e):
    return jsonify({'error': 'Resource or endpoint not found (404)'}), 404

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "Payload too large"}), 413

@app.errorhandler(415)
def unsupported_media_type(e):
    return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": "Malformed or invalid JSON syntax", "details": str(e.description)}), 400

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(e):
    return jsonify({"error": "Method not allowed for this endpoint"}), 405
