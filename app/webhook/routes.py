from flask import Blueprint, request, jsonify
from app.extensions import mongo
from datetime import datetime, timezone
import uuid

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'push':
        save_push_event(payload)
    elif event == 'pull_request':
        save_pull_request_event(payload)

    return jsonify({"status": "success"}), 200


def save_push_event(payload):
    print(f"push")
    author = payload['pusher']['name']
    to_branch = payload['ref'].split('/')[-1]
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    commit_hash = payload['after'] 
    data = {
        "action": "PUSH",
        "author": author,
        "to_branch": to_branch,
        "timestamp": timestamp,
        "request_id": commit_hash
    }
    print(data)
    mongo.db.events.insert_one(data)

def save_pull_request_event(payload):
    if payload['action'] == 'closed' and payload['pull_request']['merged']:
        print("merge")
        save_merge_event(payload)
    else:
        print(f"Pull")
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        pr_id = str(payload['pull_request']['id'])
        data = {
            "action": "PULL_REQUEST",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "request_id": pr_id
        }
        print(data)

        mongo.db.events.insert_one(data)

def save_merge_event(payload):
    author = payload['pull_request']['merged_by']['login']
    from_branch = payload['pull_request']['head']['ref']
    to_branch = payload['pull_request']['base']['ref']
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    pr_id = str(payload['pull_request']['id'])
    data = {
        "action": "MERGE",
        "author": author,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp,
        "request_id": pr_id
    }
    print(data)

    mongo.db.events.insert_one(data)


@webhook.route('/events', methods=["GET"])
def get_events():
    events = list(mongo.db.events.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
    return jsonify(events), 200