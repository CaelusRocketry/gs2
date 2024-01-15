const socket = new WebSocket('ws://' + window.location.host + '/data/');

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data)
    const header = data['header'];
    const message = data['message'];
    document.getElementById("data").innerHTML += `<h1>${header}</h1><br><p>${message}</p>`;
};

// for later
function send_message(message) {
    socket.send(JSON.stringify({
        'data': message
    }));
}