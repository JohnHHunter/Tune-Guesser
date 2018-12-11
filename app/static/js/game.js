function newSong(e){
    //1. Choose a song
        $.getJSON($SCRIPT_ROOT + '/_next_song', {
            code: e
        }, function(data) {
            //2. Change the source to the current song
            document.getElementById("song").src=data.result;
      });
}

function gameLoop(e){
    newSong(e);
        while(true){
            //3. Countdown to next song
            setTimeout(newSong, 30000)
        }
}




