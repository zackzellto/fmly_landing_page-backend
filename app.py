from flask import Flask, request, jsonify

app = Flask(__name__)

waitlist = {}


@app.route('/api/waitlist', methods=['GET', 'POST'])
def waitlist_route():
    if request.method == 'GET':
        return jsonify(list(waitlist.values()))

    elif request.method == 'POST':
        new_id = max(waitlist.keys()) + 1 if waitlist else 1
        data = request.get_json()
        waitlist[new_id] = {'id': new_id, **data}
        return jsonify(waitlist[new_id]), 201


@app.route('/api/waitlist/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def waitlist_item_route(id):
    if id not in waitlist:
        return jsonify({"error": "Not found"}), 404

    if request.method == 'GET':
        return jsonify(waitlist[id])

    elif request.method == 'PUT':
        data = request.get_json()
        waitlist[id].update(data)
        return jsonify(waitlist[id])

    elif request.method == 'DELETE':
        del waitlist[id]
        return jsonify({"success": True})


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
