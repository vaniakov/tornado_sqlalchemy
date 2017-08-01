# tornado_sqlalchemy
Hotel management example REST app.

## installation
```
git clone https://github.com/vaniakov/tornado_sqlalchemy.git
cd tornado_sqlalchemy
python3 -m virtualenv .hotel_rest
source .hotel_rest/bin/activate
pip install -r requirements.txt
```

## tests run
```
python -m tornado.test.runtests tests
```

## run app
```
python app.py --port=8900 
```

## endpoints
```
/clients/<id>
/rooms/<id>
```
