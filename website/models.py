from sqlalchemy.sql.expression import true
from . import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_admin.contrib.sqla import ModelView
from flask_table import Table, Col


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    emailAddress = db.Column(db.String, unique=True)
    cardNum = db.Column(db.VARCHAR(16), nullable=True)
    password = db.Column(db.String, nullable=False)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=True)
    phoneNumber = db.Column(db.VARCHAR(11), nullable=True)

class CustomerView(ModelView):
    form_columns = ['id', 'emailAddress', 'cardNum', 'password', 'firstName', 'lastName', 'phoneNumber']
    column_display_pk = True

class Administrator(db.Model, UserMixin):
    id = db.Column(db.VARCHAR(10), primary_key=True)
    password = db.Column(db.String, nullable=False)
    firstName = db.Column(db.String, nullable=True)
    lastName = db.Column(db.String, nullable=False)
    phoneNumber = db.Column(db.VARCHAR(11), nullable=False)
    address = db.Column(db.String, nullable=False)

class Reservation(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    totalCost = db.Column(db.Integer, nullable=False)
    checkIn = db.Column(db.DATE, nullable=False)
    checkOut = db.Column(db.DATE, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    roomNum = db.Column(db.Integer, db.ForeignKey('room.roomNum'), nullable=False)
    extras = db.relationship('Extra')

class ReservationView(ModelView):
    form_columns = ['id', 'totalCost', 'checkIn', 'checkOut', 'customer_id', 'roomNum']
    column_display_pk = True

class Room(db.Model):
    roomNum = db.Column(db.Integer, primary_key=True)
    rType = db.Column(db.String, nullable=False)
    costPerNight = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)

class RoomView(ModelView):
    form_columns = ['roomNum', 'rType']
    column_display_pk = True

class Extra(db.Model):
    orderNo = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String, nullable=True)
    bookingNum = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False, unique=True)
    extraCost = db.Column(db.Integer, nullable=False)

class ExtraView(ModelView):
    form_columns = ['orderNo', 'service', 'bookingNum', 'extraCost']
    column_display_pk = True

def __repr__(self):
    return 'Name %r' % self.id
