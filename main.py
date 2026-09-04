

from api import app
from flasgger import Swagger
import os
from api.dao import init_db

swagger = Swagger(app)
with app.app_context(): # initialisation de la bdd
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5600))
    app.run(debug=True, host='0.0.0.0', port=port) # lancer le serveur flask

