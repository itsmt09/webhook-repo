from flask_cors import CORS
from app.extensions import mongo
from app import create_app

app = create_app()
CORS(app) 
app.config["MONGO_URI"] = "mongodb://localhost:27017/database"
mongo.init_app(app)

if __name__ == '__main__': 
    app.run(debug=True)
