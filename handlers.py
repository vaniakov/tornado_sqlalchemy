import tornado.web
import tornado

from http import HTTPStatus as status

from models import Client, Room
from models import DoesNotExist, FieldError


class BaseHandler(tornado.web.RequestHandler):
    model = None
    
    def get(self, inst_id=None):
        if inst_id:
            try:
                result = self.model.get_by_id(self.db, inst_id)
            except DoesNotExist as err:
                self.set_status(status.NOT_FOUND)
                result = {'error': err.message}
        else:
            result = tornado.escape.json_encode(self.model.all(self.db))
        self.set_status(status_code=status.OK)
        self.write(result)
        
    def delete(self, inst_id):
        try:
            result = self.model.delete(self.db, inst_id)
            self.set_status(status.NO_CONTENT)
        except DoesNotExist as exc:
            self.set_status(status.NOT_FOUND)
            result = {'error': exc.message}
            self.write(result)

    def post(self, inst_id=None):
        data = tornado.escape.json_decode(self.request.body)
        try:
            result = self.model.create(self.db, data)
            self.set_status(status.CREATED)
        except FieldError as exc:
            self.db.rollback()
            self.set_status(status.BAD_REQUEST)
            result = {'error': exc.message}
        self.write(result)

    def patch(self, inst_id):
        data = tornado.escape.json_decode(self.request.body)
        try:
            result = self.model.update(self.db, inst_id, data)
            self.set_status(status.OK)
        except FieldError as exc:
            self.db.rollback()
            self.set_status(status.BAD_REQUEST)
            result = {'error': exc.message}
        except DoesNotExist as exc:
            self.set_status(status.NOT_FOUND)
            result = {'error': exc.message}
        self.write(result)

    @property
    def db(self):
        return self.application.db
    

class ClientHandler(BaseHandler):
    model = Client


class RoomHandler(BaseHandler):
    model = Room

    def _fetch_clients(self, data):
        result = []
        for client_data in data['clients']:
            result.append(Client.get_by_id(self.db, id=client_data.get('id'), to_dict=False))
        data['clients'] = result

    def post(self, client_id=None):
        data = tornado.escape.json_decode(self.request.body)
        try:
            if 'clients' in data:
                self._fetch_clients(data)
            if len(data.get('clients', [])) > data.get('places', 0):
                result = {'error': 'Number of places should be <= number of clients!'}
                self.set_status(status.BAD_REQUEST)
            else:
                result = self.model.create(self.db, data)
                self.set_status(status.CREATED)
        except (DoesNotExist, FieldError) as exc:
            self.db.rollback()
            self.set_status(status.BAD_REQUEST)
            result = {'error': exc.message}
        self.write(result)

    def patch(self, room_id):
        data = tornado.escape.json_decode(self.request.body)
        try:
            if 'clients' in data:
                self._fetch_clients(data)
            room = Room.get_by_id(self.db, room_id, to_dict=False)
            if len(data.get('clients', [])) > room.places:
                self.set_status(status.BAD_REQUEST)
                result = {'error': 'Number of clients should be >= number of places!'}
            else:
                result = self.model.update(self.db, room_id, data)
                self.set_status(status.OK)
        except (DoesNotExist, FieldError) as exc:
            self.db.rollback()
            self.set_status(status.BAD_REQUEST)
            result = {'error': exc.message}
        self.write(result)

