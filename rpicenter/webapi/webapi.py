from .rpicenter import rpicenter
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/api/post_msg/<path:uuid>",methods=['GET','POST'])
def post_msg(uuid):
    #if not request.json == None:
    #    content = request.json(silent=True)
    print(str(request.data))
    return uuid

@app.route("/")
def main():
    _result = "<ul>"
    for key, value in rpicenter.list_devices().items():
        _result = "<li>" + key + ": " + str(value) + "</li>"
    _result = _result + "</ul>"
    print(_result)
    return _result

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9003, debug=True)


