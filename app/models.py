from app import db


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, index=True)


class User(Base):
    __tablename__ = "users"
    username = db.Column(db.String(64))
    balance_rubles = db.Column(db.Float)
    balance_dollars = db.Column(db.Float)
    car_wash = db.relationship("CarWash", backref="users", lazy=True, uselist=False)
    menu = db.Column(db.String(64))
    labyrint = db.Column(db.PickleType)
    lotteries = db.relationship("UserLotteryAssociation", backref="users", lazy=True)


class CarWash(Base):
    __tablename__ = "carwashes"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    workers = db.relationship("Worker", backref="carwashes", lazy=True)


class Worker(Base):
    __tablename__ = "workers"
    name = db.Column(db.String(64))
    income = db.Column(db.Integer)
    price = db.Column(db.Integer)
    car_wash_id = db.Column(db.Integer, db.ForeignKey("carwashes.id"))
    count = db.Column(db.Integer)


class Lottery(Base):
    __tablename__ = "lotteries"
    users = db.relationship("UserLotteryAssociation", backref="lotteries", lazy=True)
    name = db.Column(db.String(64))
    contribution = db.Column(db.Integer)

class UserLotteryAssociation(Base):
    __tablename__ = "association"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lottery_id = db.Column(db.Integer, db.ForeignKey('lotteries.id'))
