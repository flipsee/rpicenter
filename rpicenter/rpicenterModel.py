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
    DeviceObjectID = CharField(db_column='DeviceObjectID', null=True, unique=True, primary_key=True)
    Slot = TextField(db_column='Slot', null=False)
    GPIOPin = DecimalField(db_column='GPIOPin', null=True)
    Location = DecimalField(db_column='Location', null=False)
    IsLocal = TextField(db_column='IsLocal', null=False)
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
        return Device.select()
    
    def clear_devices(self):
        q = Device.delete()
        q.execute()

    def add_Devices(self, rows):
        Device.insert_many(rows).execute()        

    def add_Device(self, DeviceObjectID, Slot, Location, IsLocal, GPIOPin):
        try:
            BusStop.create(DeviceObjectID=DeviceObjectID, Slot=Slot, Location=Location, IsLocal=IsLocal, GPIOPin=GPIOPin)
        except IntegrityError:
            raise ValueError("Data already exists.")
    ##### Devices Table - Stop #####

