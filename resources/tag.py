from flask.views import MethodView
from flask_smorest import Blueprint,abort
from schemas import TagSchema,AllItemTagSchema,TagAndItemSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from models.tag import TagModel
from models.store import StoreModel
from models.item import ItemModel
from models.item_tags import ItemTag
from flask_jwt_extended import jwt_required


blp = Blueprint("Tags", __name__,description="Operation on Tags")

@blp.route("/store/<int:store_id>/tag")
class Itemlist(MethodView):
    @jwt_required()
    @blp.response(201,TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,Tag_data,store_id):
        tag = TagModel(**Tag_data,store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,message=str(e))
        return tag


@blp.route("/item/<int:item_id>/tag/<string:tag_id>")
class linktagstoitem(MethodView):

    @jwt_required()
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="Error occurred during the inserting the tag")

        return tag
    
    @jwt_required()
    def delete(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="Error occurred during the inserting the tag")

        return {"message":"Item removed from tag","item": item,"tag":tag}
    

@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @jwt_required()
    @blp.response(201,TagSchema)
    def get(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        return tag
    
    @jwt_required()
    def delete(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)

        if not tag.item:
            db.session.delete(tag)
            db.session.commit()
            return ({"message": "Tag deleted successfully"})
        
        abort(400,message="Tag is associated with the item, we can't delete it.")

@blp.route("/taggedItem")
class get_tagged_item(MethodView):
    @jwt_required()
    @blp.response(201,TagSchema(many=True))
    def get(self):
        alltag=TagModel.query.all()
        return alltag