import os
from peewee import *

dbname = 'rpicenter.db'
if not os.path.exists(dbname): #check the file in the caller path
    dbnametemp = os.path.join(os.path.abspath(os.path.dirname(__file__)),dbname)
    if os.path.exists(dbnametemp): dbname = dbnametemp

database = SqliteDatabase(dbname)

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Devices(BaseModel):
    DeviceObjectID = TextField(db_column='DeviceObjectID', null=True, unique=True, primary_key=True)
    Slot = TextField(db_column='Slot', null=False)
    GPIOPin = IntegerField(db_column='GPIOPin', null=True)
    Location = TextField(db_column='Location', null=False)
    IsLocal = TextField(db_column='IsLocal', null=False)
    Type = TextField(db_column='Type', null=False)    
    class Meta:
        db_table = 'Devices'

class rpicenterBL(object):
    def __init__(self):
        database.connect()
        database.create_tables([Devices], safe=True)

    def atomic(self):
        return database.atomic()

    def close(self):
        database.close()

    ##### Devices Table - Start #####
    def get_devices(self):
        return Devices.select()
    
    def clear_devices(self):
        q = Devices.delete()
        q.execute()

    def add_Devices(self, rows):
        Devices.insert_many(rows).execute()        

    def add_Device(self, DeviceObjectID, Slot, Location, IsLocal, GPIOPin, Type):
        try:
            Devices.create(DeviceObjectID=DeviceObjectID, Slot=Slot, Location=Location, IsLocal=IsLocal, GPIOPin=GPIOPin, Type=Type)
        except IntegrityError:
            raise ValueError("Data already exists.")
    ##### Devices Table - Stop #####

