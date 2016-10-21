import urllib.request
import json      

body = {'ids': [12, 14, 50]}  

myurl = "http://rpicenter.berry/api/post_msg/12345"
req = urllib.request.Request(myurl)
req.add_header('Content-Type', 'application/json; charset=utf-8')
jsondata = json.dumps(body)
jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
req.add_header('Content-Length', len(jsondataasbytes))
print(jsondataasbytes)
response = urllib.request.urlopen(req, jsondataasbytes) 
print("Response: " + str(response))
