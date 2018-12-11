var video_link = function(e) {
    $.getJSON($SCRIPT_ROOT + '/_next_song', {
        code: e
      })
      return false;
};



