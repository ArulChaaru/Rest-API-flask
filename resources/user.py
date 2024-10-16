from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import UserSchema,UserRegisterSchema
from models.user import UserModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required,get_jwt
from blocklist import BLOCKLIST
import os
import requests


blp=Blueprint("user", __name__,description="Operation on User")


def send_simple_message(to,subject,body):
    domain = os.getenv("MAILGUN_DOMAIN")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", os.getenv("MAILGUN_API_KEY")),
        data={"from": "arul.msk11@gmail.com",
            "to": [to],
            "subject": subject,
            "text": body})



@blp.route("/userlogin")
class userlogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,userdata):
        user = UserModel.query.filter(UserModel.username == userdata["username"]).first()
        if user and pbkdf2_sha256.verify(userdata["password"],user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token":access_token}
        
        abort(401,message="Invalid credentials")



@blp.route("/user/<int:user_id>")

class Userdetails(MethodView):
    @jwt_required()
    @blp.response(201,UserSchema)
    def get(self,user_id):
        try:
            user=UserModel.query.get_or_404(user_id)
            
        except SQLAlchemyError:
            abort(404,message="User didn't exists")

        return user
    
    @jwt_required()
    def delete(self,user_id):       
        try:           
            jwt = get_jwt()
            if jwt.get("sub") !=1:
                abort(401,message="Admin Previlage required")

            user=UserModel.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(404,message="User didn't exists")

        return ({"message":"User deleted successfully"})

@blp.route("/user")
class createuser(MethodView):
    #@jwt_required()
    @blp.response(201,UserSchema(many=True))
    def get(self):
        user = UserModel.query.all()
        return user

    #@jwt_required()
    @blp.arguments(UserRegisterSchema)
    @blp.response(201,UserSchema)
    def post(self,userdata):
        try:
            user=UserModel(                
                username=userdata["username"],
                email=userdata["email"],
                password=pbkdf2_sha256.hash(userdata["password"])
        )

            db.session.add(user)
            db.session.commit()

            send_simple_message(
                to=user.email,
                subject="Successfully signed up",
                body=f"hi {user.email} successfully signed in!."
            )

        except IntegrityError:
            abort(400,message="Username already exist, please try different user name")
        except SQLAlchemyError as e:
            abort(500,message=str(e))

        return ({"message":"User added successfully",
            "id":user.id,
            "username":user.username,
            "password":user.password})
    

@blp.route("/logout")
class userlogout(MethodView):
    @jwt_required()
    def post(self):
        jti=get_jwt().get("jti")
        BLOCKLIST.add(jti)
        return {"message":"Successfully Logged out!"}