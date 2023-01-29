# Edilink

Edilink is an [Anki](https://apps.ankiweb.net/) add-on which can be used for augmenting the functionality of the built-in editor using external
applications. It exposes a [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) interface, which allows them to listen for user actions in the editor and modify
the content of the edited note. Every change is sent almost in real time, which allows the applications to supply useful
information to the user.
<!-- TODO: It can also be used as a base for other add-ons which utilize the user's browser to display content relevant
to the user's input, in a straightforward way and without difficult configuration. -->

## Data interface
In order to start, the external application has to connect to the add-on on a port specified in the add-on's configuration
(by default: 32343). Then, it can listen to incoming messages and can send its own edits. JavaScript example:
```javascript
let s = new WebSocket("ws://localhost:32343")
s.onmessage = m => console.log(m.data)
```
The data is exchanged using JSON. Both incoming and outgoing requests use the same schema:
```javascript
let data = ({
    // Read-only properties, which are not used for modifying the notes:
    "eid": "4ade0295-b19e-4cb9-8caf-c744405f99fa", // unique string identyfing the editor instance
    "id": 0, // note id (might be 0 when adding new cards)
    "guid": "OpRKE;mTtc", // note guid 
    "noteTypeId": 1592393323321, // note type id
    
    // Properties which can be used to modify the notes' content:
    "fields": { // note fields
        "Front": "Hello", 
        "Back": "World"
    },
    "tags": " tag1 tag2 " // note tags; pay attention to the spaces
})
s.send(JSON.stringify(data))
```
To clarify, the read-only fields have to be included in the write requests (because they might be required to identify
the relevant editor and note) but changing their value doesn't edit the note.

<!-- TODO
## Example app
The [example/](example/) directory contains a simple web app which essentially duplicates the functionality of the editor and displays a log of exchanged messages. If you want to try it out, install the add-on, open Anki and an editor, and open the website in your browser. Everything should connect automatically.
![This is an image](example/screenshot.png)
-->

<hr>

If you want to help in the development, or if you've found a bug, please let me know by 
[opening an issue](https://github.com/atmatto/edilink/issues/new). If you use this to create your own
tools or add-ons, reach out to me and I will add a link to it in this file. I'm curious to see your creation,
and I'm open to help or give advice if something doesn't work out as it should.