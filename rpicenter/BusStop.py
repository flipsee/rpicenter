from decimal import Decimal
try:
    from .sgDataApiBase import sgDataApiBase
    from .sgDataModel import * 
except SystemError:
    from sgDataApiBase import sgDataApiBase
    from sgDataModel import *

class BusStop(sgDataApiBase):
    def __init__(self):
        sgDataApiBase.__init__(self,"LTA")
        self.servicename = 'BusStops'

    def result(self, BusStopID):
        data = sgDataBL()
        try:
            query = data.get_busstop(BusStopID)
            _result = ''
            for entry in query:
                _result = "BusStopCode:" + entry.BusStopCode + "\n" + \
                          "RoadName:" + entry.RoadName + "\n" + \
                          "Description:" + entry.Description
        finally:
            data.close()
        return _result
    
    def refreshStoredData(self):
        results = []
        data = sgDataBL()
        try:
            print("Getting Data...")            
            with data.atomic() as txn:
                data.clear_busstops()

                while True:
                    jsonObj = self.getServiceResponse(skip=len(results))['value']
                    if jsonObj == []:
                        break
                    else:
                        data.add_busstops(jsonObj)
                        results += jsonObj

            print("Completed Getting Data, Count:" + str(len(results)))
        finally:
            data.close()        
        return self
