import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from schemas import StoreSchema,StoreUpdateSchema
from models.store import StoreModel
from db import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from flask_jwt_extended import jwt_required

blp = Blueprint("Stores", __name__,description="Operation on stores")

@blp.route("/store/<int:store_id>")
class store(MethodView):
    
    @jwt_required()
    @blp.response(201,StoreSchema)
    def get(self,store_id):
        store=StoreModel.query.get_or_404(store_id)
        return store
    
    @jwt_required()
    def delete(self,store_id):
        store=StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return ({"message": "Store deleted successfully"})
    
    @jwt_required()
    @blp.arguments(StoreUpdateSchema)
    @blp.response(201,StoreSchema)
    def put(self,store_data,store_id):
        store=StoreModel.query.get_or_404(store_id)
        try:
            if store:
                store.id =store_data['id']
                db.session.add(store)
                db.session.commit()
            else:
                abort(400,message="Store not found!, Try with valid Store ID")
        except SQLAlchemyError as e:
            abort(500,message=str(e))

        return store


@blp.route("/store")
class storelist(MethodView):
    @jwt_required()
    @blp.response(201,StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    

    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201,StoreSchema)
    def post(self,Store_data):
        store = StoreModel(**Store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Store already exists")
        except SQLAlchemyError:
            abort(500,message="Unable to add the Data in Database!")
        return store
