const socket = new WebSocket('ws://' + window.location.host + '/data/');

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['data'];
    document.getElementById("data").innerText += `\n${message}\n`;
};

// for later
function send_message(message) {
    socket.send(JSON.stringify({
        'data': message
    }));
}