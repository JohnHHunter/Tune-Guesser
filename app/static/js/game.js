var previousSong = "?";

function newSong(e){
    console.log("New Song");
    $('#result').text("Previous Song: "+ previousSong);
    //1. Choose a song
        $.getJSON($SCRIPT_ROOT + '/_next_song', {
            code: e
        }, function(data) {
            previousSong = data.song_name;
            document.getElementById("song").src=data.result;
      });
}

function game(e){
    setInterval(newSong, 30000, e);
}
