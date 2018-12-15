var previousSong = "?";
var isStarted = false;
var looped = false;
console.log("looped init - " + looped);

function newSong(e){
    $('#previous').text(previousSong);
    $('#correct').text("");
        $.getJSON($SCRIPT_ROOT + '/_next_song', {
            code: e
        }, function(data) {
            if(data.song_name === previousSong){
                newSong(e)
            }
            else{
                previousSong = data.song_name;
                document.getElementById("song").src=data.result;
                document.getElementById("song").width=704;
                document.getElementById("song").height=369;
            }

      });
}

function game(e){
    document.getElementById('start').style.visibility = 'hidden';
    newSong(e);
    setInterval(newSong, 30000, e);
}

$(document).ready(function () {
    setInterval(update, 1000);

    function update(){
        $.getJSON($SCRIPT_ROOT + '/_update', {
        }, function(data) {
            var toAdd = '';
            isStarted = data.started;
            console.log(isStarted);
            for(var i=0; i<data.players.length; i++){
                toAdd += '<div class="player-background">' + data.players[i].username + ': ' + data.players[i].pointsInRoom + '</div>';
            }
            $('#player_list').html(toAdd);

            if(isStarted){
                if(!looped){
                    gameLoop();
                    looped = true;
                }
            }
      });

    }

    function gameLoop(){
        syncSong();
        setInterval(syncSong, 30010)
    }

    function syncSong(){
        console.log("about to change");
        $.getJSON($SCRIPT_ROOT + '/_sync_song', {
        }, function(data) {
            document.getElementById("song").src=data.result;
            document.getElementById("song").width=704;
            document.getElementById("song").height=369;
      });
    }

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
