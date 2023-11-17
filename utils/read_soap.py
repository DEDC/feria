# Python
import json
# zeep
from zeep import Client

class GetSOAPData:
    def __init__(self, client_url, service_name, port_name, params={}):
        self.client_url = client_url
        self.service_name = service_name
        self.port_name = port_name
        self.params = {'V_regcve': '', 'V_unicve': '', 'V_almcve': '', 'V_movcve': '', 'V_fecha': '', 'V_anio': 2023}
        self.create_client()
    
    def create_client(self):
        client = Client(self.client_url, service_name=self.service_name, port_name=self.port_name)
        self.response = client.service.Execute(**self.params)
        # print(self.response, 'bieen')
    
    def to_json(self):
        return json.loads(self.response)
    
    

# c = GetSOAPData(
#     client_url='http://cloud.diconsa.gob.mx/OrdenSIACJavaEnvironment/servlet/agetmovtossiac?wsdl', 
#     service_name='GetMovtosSIAC', 
#     port_name='GetMovtosSIACSoapPort')



























# {
#     "status": "validated", 
#     "validations": [
#         {
#             "date": "27/06/2023", 
#             "time": "11:15:12", 
#             "status": "pending",
#             "validator": "David Domínguez",
#             "uuid": "609b25ab-aac3-4bd6-8192-a97789235dcb",
#             "fields": [
#                 {"field": "contrato", "comments": "Sube un nuevo documento"}
#             ]
#             , , },
#     ]
# }