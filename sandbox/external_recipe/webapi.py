from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/api/post_msg/<path:uuid>",methods=['GET','POST'])
def post_msg(uuid):
    #if not request.json == None:
    #    content = request.json(silent=True)
    print(str(request.data))
    return uuid

@app.route("/")
def hello():
    return "Hi, this is rpicenter Web API landing page, available method:"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9003, debug=True)


