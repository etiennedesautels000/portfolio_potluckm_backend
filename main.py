

from api import app
from api.dao import init_db
from flasgger import Swagger
import os

if __name__ == "__main__":
    swagger = Swagger(app)
    with app.app_context(): # initialisation de la bdd
        init_db()
    port = int(os.environ.get('PORT', 5600))
    app.run(debug=True, host='0.0.0.0', port=port) # lancer le serveur flask

