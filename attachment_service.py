# File Attachment microservice
# CS361 Team 11
#
# Uses ZeroMQ with JSON messages on port 5558.

import base64
import json
import os
import zmq

PORT = 5558
MAX_SIZE = 25 * 1024 * 1024   # 25 MB
FOLDER = "attachments"


def error(message):
    return {"status": "error", "message": message}


def is_safe_name(name):
    # these names get used as folder and file names, so don't allow anything
    # that could point somewhere outside the attachments folder
    name = str(name)
    if name == "" or name == ".":
        return False
    for bad in ["/", "\\", ":", ".."]:
        if bad in name:
            return False
    return True


def attach_file(app, item_id, file_name, file_data):
    try:
        file_bytes = base64.b64decode(file_data)
    except Exception:
        return error('"file_data" is not valid base64')

    if len(file_bytes) > MAX_SIZE:
        return error("File is larger than 25 MB")

    item_folder = os.path.join(FOLDER, app, str(item_id))
    os.makedirs(item_folder, exist_ok=True)
    with open(os.path.join(item_folder, file_name), "wb") as f:
        f.write(file_bytes)

    return {"status": "success", "message": f"{file_name} attached to item {item_id}"}


def view_files(app, item_id):
    item_folder = os.path.join(FOLDER, app, str(item_id))
    files = []
    if os.path.exists(item_folder):
        for file_name in sorted(os.listdir(item_folder)):
            size = os.path.getsize(os.path.join(item_folder, file_name))
            files.append({"file_name": file_name, "size_bytes": size})

    return {"status": "success", "item_id": item_id, "files": files}


def remove_file(app, item_id, file_name):
    path = os.path.join(FOLDER, app, str(item_id), file_name)
    if not os.path.isfile(path):
        return error(f"No file named {file_name} on item {item_id}")

    os.remove(path)
    return {"status": "success", "message": f"{file_name} removed from item {item_id}"}


def handle_request(message):
    # turn the JSON string into a dictionary
    try:
        request = json.loads(message)
    except json.JSONDecodeError:
        return error("Request is not valid JSON")
    if type(request) != dict:
        return error("Request is not valid JSON")

    action = request.get("action")
    app = request.get("app")
    item_id = request.get("item_id")
    file_name = request.get("file_name")
    file_data = request.get("file_data")

    # check the parameters before doing anything
    if action not in ["attach", "view", "remove"]:
        return error('"action" must be "attach", "view", or "remove"')
    if type(app) != str or app == "":
        return error('"app" is required and must be a string')
    if type(item_id) not in [str, int] or item_id == "":
        return error('"item_id" is required and must be a string or number')
    if not is_safe_name(app) or not is_safe_name(item_id):
        return error('"app" and "item_id" cannot contain / \\ : or ..')

    if action == "view":
        return view_files(app, item_id)

    # attach and remove both need a file name
    if type(file_name) != str or file_name == "":
        return error(f'"file_name" is required for "{action}" and must be a string')
    if not is_safe_name(file_name):
        return error('"file_name" must be a plain file name, not a path')

    if action == "remove":
        return remove_file(app, item_id, file_name)

    if type(file_data) != str:
        return error('"file_data" is required for "attach" and must be base64 text')
    return attach_file(app, item_id, file_name, file_data)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print(f"File Attachment microservice listening on port {PORT}")

    while True:
        message = socket.recv_string()
        # only print the start of the message because file data can be huge
        print("Received request:", message[:200])

        reply = json.dumps(handle_request(message))

        socket.send_string(reply)
        print("Sent reply:      ", reply)
        print()


if __name__ == "__main__":
    main()
