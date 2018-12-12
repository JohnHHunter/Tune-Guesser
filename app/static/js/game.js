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

function chat(e){
    $.getJSON($SCRIPT_ROOT + '/_chat_message', {
        msg: $('input[name="chat"]').val(),
        code: e
      }, function(data) {
        if(data.result){
            $('#correct').text("You guessed the song correctly");
        }
      });
}
