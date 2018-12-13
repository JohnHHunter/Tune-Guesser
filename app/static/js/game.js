var previousSong = "?";

function newSong(e){
    $('#previous').text("Previous Song: "+ previousSong);
    $('#correct').text("");
        $.getJSON($SCRIPT_ROOT + '/_next_song', {
            code: e
        }, function(data) {
            previousSong = data.song_name;
            document.getElementById("song").src=data.result;
      });
}

function game(e){
    document.getElementById('start').style.visibility = 'hidden';
    newSong(e);
    setInterval(newSong, 30000, e);
}

$(document).ready(function () {
    function sendMessage(){
        socket.send($('#myMessage').val());
        $('#myMessage').val('');
    }

    var socket = io.connect('http://127.0.0.1:5000');

    socket.on('connect', function(){
    });

    socket.on('message', function (msg) {
       $("#messages").append('<li>' + msg +'</li>')
    });

    $('#sendButton').on('click', function (){
        socket.send($('#myMessage').val());
        $('#myMessage').val('');
    });

   $(document).keypress(function(event){
	var keycode = (event.keyCode ? event.keyCode : event.which);
	if(keycode == '13'){
		sendMessage();
	}

});


});
