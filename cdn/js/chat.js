function newMessage() {
  text = document.getElementById("text").value;
  if (text === "") return;
  const data = {
    "text": text,
    "user": {
      "name": document.getElementById("user-name").value,
      "pic": document.getElementById("user-pic").value
    }
  };
  socket.emit("new_message", data);
  document.getElementById("text").value = "";
};

var socket = io();
$(document).ready(function() {
  socket.on('connect', function() {
    socket.emit('connected', {
      data: 'I\'m connected!'
    });
  });

  $('.text-input').keypress((e) => {
    if (e.which === 13) {
      newMessage();
    }
  });

  socket.on('message', function(data) {
    if (data["text"] === null) {
      return
    };
    console.log(data);
    messages = document.getElementsByClassName("message-container");
    if (messages.length > 4) {
      messages[0].remove();
    };
    var msgContainer = document.createElement("div");
    msgContainer.classList.add("message-container");
    msgContainer.innerHTML = `
<div class="pic-message">
<img class="message" src="${data['user']['pic']}">
</div>
<div class="message">
<a class="user"><strong>${data["user"]["name"]}:</strong></a> <a class="text">${data["text"]}</a>
</div>
<br>
`
    document.getElementById("messages").appendChild(msgContainer);
  });
});
