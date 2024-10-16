from marshmallow import Schema,fields

class PlainItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    name=fields.Str(required=True)
    id=fields.Str(dump_only=True)


class PlainTagSchema(Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str()

class StoreUpdateSchema(Schema):
    id=fields.Int(required=True)

class AllItemTagSchema(Schema):
    id=fields.Int(dump_only=True)
    item_id=fields.Int(dump_only=True)
    tag_id=fields.Int(dump_only=True)

class ItemUpdateSchema(Schema):
    name=fields.Str()
    price=fields.Float()
    store_id=fields.Int()

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True,load_only=True)
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()),dump_only=True)

class StoreSchema(PlainStoreSchema):
    items= fields.List(fields.Nested(PlainItemSchema()),dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()),dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    item=fields.List(fields.Nested(PlainItemSchema(),dump_only=True))

class TagAndItemSchema(Schema):
    message=fields.Str()
    item=fields.Nested(ItemSchema)
    tag=fields.Nested(TagSchema)


class UserSchema(Schema):
    message=fields.Str(dump_only=True)
    id=fields.Int(dump_only=True)    
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True,load_only=True)