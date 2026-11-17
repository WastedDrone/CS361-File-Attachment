
# Test program for File Attachment microservice
# CS361
# Uses ZeroMQ with JSON messages on port 5558.
# How to run:
# Terminal 1: python3 attachment_service.py
# Terminal 2: python3 test_attachment.py

import json
import base64
import zmq

APP = "test_program"


def send_request(socket, request):
    print("Request sent:", json.dumps(request))
    socket.send_string(json.dumps(request))

    reply = json.loads(socket.recv_string())
    print("Reply received:", json.dumps(reply))
    print()


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558")

    print("Connected to File Attachment microservice\n")

    # Test 1: Attach a file
    print("Test 1: Attach a file")

    file_data = base64.b64encode(b"Hello classssss").decode("utf-8")

    send_request(socket, {
        "action": "attach",
        "app": APP,
        "item_id": 5,
        "file_name": "test.txt",
        "file_data": file_data
    })

    # Test 2: View files
    print("Test 2: View files")
    send_request(socket, {
        "action": "view",
        "app": APP,
        "item_id": 5
    })

    # Test 3: Remove a file
    print("Test 3: Remove a file")
    send_request(socket, {
        "action": "remove",
        "app": APP,
        "item_id": 5,
        "file_name": "test.txt"
    })

    # Test 4: View files after removing
    print("Test 4: View files after removing")
    send_request(socket, {
        "action": "view",
        "app": APP,
        "item_id": 5
    })

    # Test 5: Remove a file that does not exist
    print("Test 5: File does not exist")
    send_request(socket, {
        "action": "remove",
        "app": APP,
        "item_id": 5,
        "file_name": "missing.txt"
    })

    socket.close()
    context.term()

    print("All tests finished.")


if __name__ == "__main__":
    main()
