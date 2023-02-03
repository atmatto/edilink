import json
import uuid

from aqt import gui_hooks, mw, qt, editor, utils
from PyQt6 import QtWebSockets, QtNetwork

ws_server: QtWebSockets.QWebSocketServer | None = None
sockets: list[QtWebSockets.QWebSocket] = []


# add the new socket to `sockets` and connect needed events
def new_connection():
    global ws_server, sockets
    socket = ws_server.nextPendingConnection()
    qt.qconnect(socket.textMessageReceived, receive_note)
    sockets.append(socket)


# send a message to all open sockets
def broadcast(text: str):
    global sockets
    for s in sockets:
        s.sendTextMessage(text)


# initialize WebSockets server
def init_ws() -> bool:
    global ws_server
    ws_server = QtWebSockets.QWebSocketServer("stol remote", QtWebSockets.QWebSocketServer.SslMode.NonSecureMode, mw.window())
    ws_server.setSupportedSubprotocols(["edilink"])
    qt.qconnect(ws_server.newConnection, new_connection)
    return ws_server.listen(QtNetwork.QHostAddress("localhost"), 32343)


# dictionary of all known editors, the key is the editor's id
editors: dict[str, editor.Editor] = {}


# process an incoming request
def receive_note(text: str):
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Edilink: Failed to decode request")

    if data is not None:
        ed = editors[data["eid"]]
        if ed is None:
            print("Edilink: Unknown editor ID: %s" % data["eid"])
        elif data["guid"] != ed.note.guid:
            print("Edilink: Tried to edit note with a different GUID (expected %s, got %s)" % (ed.note.guid, data["guid"]))
        else:
            for f, v in data["fields"].items():
                ed.note[f] = v
            ed.note.set_tags_from_str(data["tags"])
        # make the editor load the changes
        ed.loadNoteKeepingFocus()


# this class works around the fact that call_after_note_saved doesn't supply the editor to the callback
class Sender:
    ed: editor.Editor

    # broadcast part of the edited note's state
    def send_state(self):
        n = self.ed.note
        data = {
            # metadata
            "eid": self.ed.eid,
            "id": n.id,
            "guid": n.guid,
            "noteTypeId": n.mid,
            # editable content
            "fields": {item[0]: item[1] for item in n.items()},
            "tags": n.string_tags()
        }
        broadcast(json.dumps(data))

    def __init__(self, ed: editor.Editor):
        self.ed = ed


def on_event(handled, _, context):
    global editors
    # only care about the event if the context is an editor
    if isinstance(context, editor.Editor):
        if not hasattr(context, "eid"):
            # save the editor for later using a unique id (will be needed for processing write requests)
            context.eid = str(uuid.uuid4())
            editors[context.eid] = context
            context.sender = Sender(context)
        # the note has to be saved first, otherwise the data would be outdated
        context.call_after_note_saved(context.sender.send_state, True)
    return handled


if not init_ws():
    utils.showCritical("Edilink: Failed to start the WebSocket server.")
else:
    gui_hooks.webview_did_receive_js_message.append(on_event)
