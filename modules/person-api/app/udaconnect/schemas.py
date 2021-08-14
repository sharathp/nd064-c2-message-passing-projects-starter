from app.udaconnect.models import Person
from marshmallow import Schema, fields


class PersonSchema(Schema):
    id = fields.Integer()
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    company_name = fields.String(required=True)

    class Meta:
        model = Person
