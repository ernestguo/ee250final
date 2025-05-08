from flask import Flask, request, jsonify
import time
from gps_reader import start_event, timeout_event

app = Flask(__name__)

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    sid = data.get('id')
    if sid is None:
        return jsonify({'error':'missing id'}), 400
    # invoke GPS reader callback
    start_event(sid)
    return jsonify({'status':'started', 'id': sid}), 200

@app.route('/timeout', methods=['POST'])
def timeout():
    data = request.get_json()
    tid = data.get('id')
    if tid is None:
        return jsonify({'error':'missing id'}), 400
    timeout_event(tid)
    return jsonify({'status':'timed out', 'id': tid}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)