from flask import Flask,jsonify
from flask_smorest import Api
from resources.store import blp as StoreBluePrint
from resources.item import blp as ItemBluePrint
from resources.tag import blp as TagBluePrint
from resources.user import blp as UserBluePrint
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from flask_migrate import Migrate
from db import db
import os
import secrets


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.1.0"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    migrate = Migrate(app,db)
    api = Api(app)

    #app.config["JWT_SECRET_KEY"]=secrets.SystemRandom().getrandbits(128)
    app.config["JWT_SECRET_KEY"]="jose"
    jwt=JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoke_token_callback(jwt_header,jwt_payload):
        return (
            jsonify(
                {"description":"The token has been revoked","error":"Token Revoked"}
            ),401,
        )
    
    @jwt.additional_claims_loader
    def add_claims_to_JWT(identity):
        if identity==1:
            return {"is_admin":True}
        else:
            return {"is_admin":False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return (
            jsonify({"message":"The token expired.","error":"token_expired"}),
            401,
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message":"Signature verification failed.", "error":"Invalid_token."}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description":"Request does not contain the access token",
                    "error":"authorization_required",
                    }
            ),
            401,
        )



    with app.app_context():
        # Uncomment these lines for development use only
        # db.drop_all()
        # db.create_all()

        # Ensure models are imported here
        from models.store import StoreModel
        from models.item import ItemModel   # Ensure your models are defined
        from models.tag import TagModel
        from models.item_tags import ItemTag
        from models.user import UserModel

        #db.create_all()

    # Register blueprints
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)
    # UserBluePrint

    return app
