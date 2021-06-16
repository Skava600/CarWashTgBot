from app import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64))
    balance_rubles = db.Column(db.Float)
    balance_dollars = db.Column(db.Float)
    car_wash = db.relationship("CarWash", backref="users", lazy=True, uselist=False)
    menu = db.Column(db.String(64))
    labyrint = db.Column(db.PickleType)


class CarWash(db.Model):
    __tablename__ = "carwashes"
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    workers = db.relationship("Worker", backref="carwashes", lazy=True)


class Worker(db.Model):
    __tablename__ = "workers"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))
    income = db.Column(db.Integer)
    price = db.Column(db.Integer)
    car_wash_id = db.Column(db.Integer, db.ForeignKey("carwashes.id"))
    count = db.Column(db.Integer)
