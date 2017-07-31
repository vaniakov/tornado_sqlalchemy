import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()
log = logging.getLogger(__name__)

clients = Table('room_client', Base.metadata,
    Column('room_id', Integer, ForeignKey('rooms.id')),
    Column('client_id', Integer, ForeignKey('clients.id'))
)


class DoesNotExist(Exception):

    def __init__(self, class_name, **params):
        self.message = "{0} with provided params not found:{1}".format(class_name, params)
        super().__init__(self.message)


class FieldError(TypeError):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ModelMixin:

    @classmethod
    def get_by_id(cls, session, id, to_dict=True):
        result = session.query(cls).filter(cls.id == id).first()
        if not result:
            raise DoesNotExist(cls.__name__, id=id)
        if to_dict:
            result = result.to_dict()
        return result

    @classmethod
    def all(cls, session):
        return cls.instances_to_dict(session.query(cls).all())

    @classmethod
    def instances_to_dict(cls, instances_list):
        return [inst.to_dict() for inst in instances_list]

    @classmethod
    def create(cls, session, data_dict, commit=True, close=False, to_dict=True):
        try:
            inst = cls(**data_dict)
            session.add(inst)
            if commit:
                session.commit()
        except (TypeError, IntegrityError) as err:
            raise FieldError(err.args[0])
        if close:
            session.close()
        result = inst
        if to_dict:
            result = inst.to_dict()
        return result

    @classmethod
    def update(cls, session, id, data_dict, commit=True, close=False):
        inst = cls.get_by_id(session, id, to_dict=False)
        try:
            for key, value in data_dict.items():
                setattr(inst, key, value)
            if commit:
                session.commit()
        except (IntegrityError, ValueError) as err:
            raise FieldError(err.args[0])

        if close:
            session.close()
        return inst.to_dict()

    @classmethod
    def delete(cls, session, id, commit=True, close=False):
        inst = cls.get_by_id(session, id, to_dict=False)
        session.delete(inst)
        if commit:
            session.commit()
        if close:
            session.close()


class Client(Base, ModelMixin):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))

    def __repr__(self):
        return '<Client: %s %s>' % (self.first_name, self.last_name)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name
        }


class Room(Base, ModelMixin):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True)
    places = Column(Integer)
    price_day = Column(Float(precision=2))
    clients = relationship('Client', secondary=clients,
                           backref=backref('room', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'places': self.places,
            'price_day': self.price_day,
            'clients': Room.instances_to_dict(self.clients)
        }

    def __repr__(self):
        return '<Room: №%s %s places, %s$ per day>' % (self.number, self.places,
                                                       self.price_day)


def init_db(engine):
    Base.metadata.create_all(bind=engine)


def create_session(db_path, debug=False):
    engine = create_engine(
        db_path, convert_unicode=True, echo=debug)
    init_db(engine)
    return scoped_session(sessionmaker(bind=engine))

if __name__ == '__main__':
    db = create_session('sqlite:///:memory:', True)
    client = Client(first_name='John', last_name='Doe')
    client2 = Client(first_name='Lilly', last_name='Doe')
    db.add(client)
    db.add(client2)

    room = Room(number=333, places=2, price_day=40.0, clients=[client, client2])
    db.commit()
    print(room)
    print(room.to_dict())

    client = Client(adsf='adf')
    db.add(client)
    db.commit()

