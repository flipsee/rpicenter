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
    IsLocal = IntegerField(db_column='IsLocal', null=False)
    Type = TextField(db_column='Type', null=False)    
    class Meta:
        db_table = 'Devices'

class DeviceReading(BaseModel):
    DeviceObjectID = TextField(db_column='DeviceObjectID', null=False)
    ReadingDateTime = TextField(db_column='ReadingDateTime', null=False)
    Parameter = TextField(db_column='Parameter', null=False)
    Value = DoubleField(db_column='Value', null=False)
    Unit = TextField(db_column='Unit', null=True)
    class Meta:
        db_table = 'DeviceReading'
        primary_key = CompositeKey('DeviceObjectID', 'ReadingDateTime', 'Parameter', 'Unit')

class rpicenterBL(object):
    def __init__(self):
        database.connect()
        database.create_tables([Devices], safe=True)
        database.create_tables([DeviceReading], safe=True)

    def atomic(self):
        return database.atomic()

    def close(self):
        database.close()

    ##### Devices Table - Start #####
    def get_Devices(self):
        return Devices.select()
    
    def clear_Devices(self):
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

    def get_DeviceReading(self):
        return DeviceReading.select()

    def clear_DeviceReading(self):
        q = DeviceReading.delete()
        q.execute()

    def add_DeviceReading(self, rows):
        Devices.insert_many(rows).execute()

    def add_DeviceReading(self, DeviceObjectID, ReadingDateTime, Parameter, Value, Unit):
        try:
            DeviceReading.create(DeviceObjectID=DeviceObjectID, ReadingDateTime=ReadingDateTime, Parameter=Parameter, Value=Value, Unit=Unit)
        except IntegrityError:
            raise ValueError("Data already exists.")
