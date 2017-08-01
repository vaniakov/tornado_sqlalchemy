import json

from tornado.testing import AsyncHTTPClient, AsyncHTTPTestCase, AsyncTestCase

import app as application
import models
import handlers
import os


class TestOptions(object):
    def __init__(self, debug=True, db_path='sqlite:///test.db', port=8901):
        self.debug = debug
        self.db_path = db_path
        self.port = port


class TestClients(AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        cls.options = TestOptions(debug=False)
        cls.app = application.Application(cls.options)
        cls.db = cls.app.db

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        self.client_data1 = {'first_name': 'John', 'last_name': 'Doe'}
        self.client_data2 = {'first_name': 'Fred', 'last_name': 'Mercury'}
        super().setUp()

    def tearDown(self):
        self.db.rollback()
        super().tearDown()

    def get_app(self):
        return self.app

    def test_clients_all(self):
        models.Client.create(self.db, self.client_data1, commit=False)
        models.Client.create(self.db, self.client_data2, commit=False)
        response = self.fetch('/clients/')
        parsed_body = json.loads(response.body.decode())
        self.assertEqual(response.code, 200)
        self.assertEqual(len(parsed_body), 2)
        self.assertEqual(parsed_body[0]['id'], 1)
        self.assertEqual(parsed_body[0]['first_name'],
                         self.client_data1['first_name'])
        self.assertEqual(parsed_body[0]['last_name'],
                         self.client_data1['last_name'])
    def test_clients_detail(self):
        models.Client.create(self.db, self.client_data1, commit=False)
        response = self.fetch('/clients/1')
        parsed_body = json.loads(response.body.decode())
        self.assertEqual(response.code, 200)
        self.assertEqual(parsed_body['id'], 1)
        self.assertEqual(parsed_body['first_name'],
                         self.client_data1['first_name'])
        self.assertEqual(parsed_body['last_name'],
                         self.client_data1['last_name'])

    def test_clients_create(self):
        response = self.fetch('/clients/', body=json.dumps(self.client_data1),
                              method='POST')
        parsed_body = json.loads(response.body.decode())
        self.assertEqual(response.code, 201)
        self.assertEqual(parsed_body['id'], 1)
        self.assertEqual(parsed_body['first_name'],
                         self.client_data1['first_name'])
        self.assertEqual(parsed_body['last_name'],
                         self.client_data1['last_name'])
        models.Client.delete(self.db, parsed_body['id'], commit=True)

    def test_clients_update(self):
        models.Client.create(self.db, self.client_data1, commit=False)
        response = self.fetch('/clients/1', body=json.dumps({'last_name': 'changed'}),
                              method='PATCH')
        parsed_body = json.loads(response.body.decode())
        client = models.Client.get_by_id(self.db, parsed_body['id'], to_dict=False)

        self.assertEqual(response.code, 200)
        self.assertEqual(parsed_body['first_name'],
                         self.client_data1['first_name'])
        self.assertEqual(parsed_body['last_name'],
                         'changed')
        self.assertEqual(client.last_name, 'changed')
        self.db.delete(client)
        self.db.commit()

    def test_client_delete(self):
        models.Client.create(self.db, self.client_data1, commit=False)
        response = self.fetch('/clients/1', method='DELETE')
        with self.assertRaises(models.DoesNotExist):
            models.Client.get_by_id(self.db, 1, to_dict=False)
        self.assertEqual(response.code, 204)


class TestRooms(AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        cls.options = TestOptions(debug=False)
        cls.app = application.Application(cls.options)
        cls.db = cls.app.db

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        super().setUp()
        client_data1 = {'first_name': 'John', 'last_name': 'Doe'}
        client_data2 = {'first_name': 'Fred', 'last_name': 'Mercury'}
        self.client2 = models.Client.create(self.db, client_data2, commit=True, to_dict=False)
        self.client1 = models.Client.create(self.db, client_data1, commit=True, to_dict=False)

        self.room_data1 = {'number': 444, 'price_day': 34.4, 'places': 4}
        self.room_data2 = {'number': 333, 'price_day': 34.4, 'places': 1}

    def tearDown(self):
        self.db.rollback()
        self.db.delete(self.client1)
        self.db.delete(self.client2)
        self.db.commit()
        super().tearDown()

    def get_app(self):
        return self.app

    def test_rooms_all(self):
        models.Room.create(self.db, self.room_data1, commit=False)
        models.Room.create(self.db, self.room_data2, commit=False)
        response = self.fetch('/rooms/')
        parsed_body = json.loads(response.body.decode())
        self.assertEqual(response.code, 200)
        self.assertEqual(len(parsed_body), 2)
        self.assertEqual(parsed_body[0]['number'],
                         self.room_data1['number'])

    def test_clients_detail(self):
        models.Room.create(self.db, self.room_data1, commit=False)
        response = self.fetch('/rooms/1')
        parsed_body = json.loads(response.body.decode())
        self.assertEqual(response.code, 200)
        self.assertEqual(parsed_body['id'], 1)
        self.assertEqual(parsed_body['number'],
                         self.room_data1['number'])

    def test_room_create(self):
        response = self.fetch('/rooms/', body=json.dumps(self.room_data1),
                              method='POST')
        parsed_body = json.loads(response.body.decode())
        self.assertEqual(response.code, 201)
        self.assertEqual(parsed_body['id'], 1)
        self.assertEqual(parsed_body['number'],
                         self.room_data1['number'])
        self.assertEqual(parsed_body['places'],
                         self.room_data1['places'])
        models.Room.delete(self.db, parsed_body['id'], commit=True)

    def test_rooms_update(self):
        models.Room.create(self.db, self.room_data1, commit=False)
        response = self.fetch('/rooms/1', body=json.dumps({'places': 33}),
                              method='PATCH')
        parsed_body = json.loads(response.body.decode())
        client = models.Room.get_by_id(self.db, parsed_body['id'], to_dict=False)

        self.assertEqual(response.code, 200)
        self.assertEqual(parsed_body['number'],
                         self.room_data1['number'])
        self.assertEqual(parsed_body['places'],
                         33)
        self.assertEqual(client.places, 33)
        self.db.delete(client)
        self.db.commit()

    def test_client_delete(self):
        models.Room.create(self.db, self.room_data1, commit=False)
        response = self.fetch('/rooms/1', method='DELETE')
        with self.assertRaises(models.DoesNotExist):
            models.Room.get_by_id(self.db, 1, to_dict=False)
        self.assertEqual(response.code, 204)

    def test_rooms_update_add_clients(self):
        models.Room.create(self.db, self.room_data1, commit=False)
        response = self.fetch('/rooms/1',
                              body=json.dumps({'clients': [
                                  {'id': self.client1.id},
                                  {'id': self.client2.id}
                              ]}
                              ),
                              method='PATCH')
        parsed_body = json.loads(response.body.decode())
        room = models.Room.get_by_id(self.db, parsed_body['id'], to_dict=False)

        self.assertEqual(response.code, 200)
        self.assertEqual(len(parsed_body['clients']), 2)
        self.assertEqual(parsed_body['clients'][0]['id'], self.client1.id)
        self.db.delete(room)
        self.db.commit()

    def test_rooms_update_add_too_much_clients(self):
        self.room_data2['places'] = 1
        created_room = models.Room.create(self.db, self.room_data2, commit=True, to_dict=False)
        response = self.fetch('/rooms/%s' % created_room.id,
                              body=json.dumps({'clients': [
                                  {'id': self.client1.id},
                                  {'id': self.client2.id}
                              ]}
                              ),
                              method='PATCH')
        parsed_body = json.loads(response.body.decode())
        room = models.Room.get_by_id(self.db, created_room.id, to_dict=False)

        self.assertEqual(response.code, 400)
        self.assertTrue('error' in parsed_body)
        self.db.delete(room)
        self.db.commit()

    def test_create_room_duplicate_number(self):
        created_room = models.Room.create(self.db, self.room_data1, commit=True)
        response = self.fetch('/rooms/',
                              body=json.dumps(self.room_data1), method='POST')
        parsed_body = json.loads(response.body.decode())
        room = models.Room.get_by_id(self.db, created_room['id'], to_dict=False)
        self.assertEqual(response.code, 400)
        self.assertTrue('error' in parsed_body)
        self.db.delete(room)
        self.db.commit()
