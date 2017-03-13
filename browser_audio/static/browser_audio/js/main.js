window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null,
    realAudioInput = null,
    inputPoint = null,
    audioRecorder = null,
    rafID = null,
    analyserContext = null;
var canvasWidth, canvasHeight;
var recIndex = 0;
var hours = minutes = seconds = milliseconds = 0;
var prev_hours = prev_minutes = prev_seconds = prev_milliseconds = undefined;
var timeUpdate;
var up = new Audio(m_up);
var down = new Audio(m_down);
var m_on = false;
var m;
var num_clicks = 0;
var bpm;
var subdivision;
var mr = false,
    ci = false,
    as = false,
    recording = false;

function updateTime(prev_minutes, prev_seconds){
    var startTime = new Date();
    timeUpdate = setInterval(function () {
        var timeElapsed = new Date().getTime() - startTime.getTime();
        minutes = parseInt(timeElapsed / 1000 / 60) + prev_minutes;
        if (minutes > 60) minutes %= 60;
        seconds = parseInt(timeElapsed / 1000) + prev_seconds;
        if (seconds >= 60) seconds %= 60;
        setStopwatch(minutes, seconds);
    }, 25);
}

function setStopwatch(minutes, seconds){
    $("#minutes").html(prependZero(minutes, 2));
    $("#seconds").html(prependZero(seconds, 2));
}

function prependZero(time, length) {
    time = new String(time);
    return new Array(Math.max(length - time.length + 1, 0)).join("0") + time;
}

function saveAudio() {
    audioRecorder.exportWAV( doneEncoding );
    // could get mono instead by saying
    // audioRecorder.exportMonoWAV( doneEncoding );
}

function gotBuffers( buffers ) {
    var canvas = document.getElementById( "wavedisplay" );

    //drawBuffer( canvas.width, canvas.height, canvas.getContext('2d'), buffers[0] );

    // the ONLY time gotBuffers is called is right after a new recording is completed - 
    // so here's where we should set up the download.
    audioRecorder.exportWAV( doneEncoding );
}

function doneEncoding( blob ) {
    Recorder.setupDownload( blob, "myRecording" + ((recIndex<10)?"0":"") + recIndex + ".wav" );
    recIndex++;
}

function toggleRecording() {
    if (recording) {
        // stop recording
        document.getElementById('saving').style.display = "inline-block";
        audioRecorder.stop();
        $("#record_button").removeClass("recording");
        audioRecorder.getBuffers( gotBuffers );
        clearInterval(timeUpdate);
        recording = false;
    } else {
        // start recording
        if (!audioRecorder)
            return;
        if (mr) {
            startMetronome();
        }
        $("#record_button").addClass("recording");
        audioRecorder.clear();
        audioRecorder.record();
        updateTime(0,0);
        recording = true;
    }
}

function deleteAudio(file_url, id) {
    $.ajax({
        type: 'POST',
        url: '/audio/delete_file/',
        data: {
            'file_url': file_url,
            'id': id,
        },
        success: function(r) {
            location.reload();
        },
        error: function(r) {
            alert(r);
        }
    });
}

function logvalue(position, height) {
    var minp = 0;
    var maxp = 255;
    var minv = Math.log(1);
    var maxv = Math.log(height);
    var scale = (maxv-minv) / (maxp-minp);
    return Math.exp(minv + scale*(position-minp));
}

function updateAnalysers(time) {
    if (!analyserContext) {
        var canvas = document.getElementById("analyser");
        canvasWidth = canvas.width;
        canvasHeight = canvas.height;
        analyserContext = canvas.getContext('2d');
    }

    // analyzer draw code here
    {
        var SPACING = 3;
        var BAR_WIDTH = 10;
        var numBars = Math.round(canvasWidth / SPACING);
        var freqByteData = new Uint8Array(analyserNode.frequencyBinCount);
       
        analyserNode.getByteFrequencyData(freqByteData); 

        analyserContext.clearRect(0, 0, canvasWidth, canvasHeight);
        analyserContext.fillStyle = '#F6D565';
        analyserContext.lineCap = 'round';
        var multiplier = analyserNode.frequencyBinCount / numBars;
        var magnitude = 0;
        for (var i = 0; i < analyserNode.frequencyBinCount; i++) {
            
            if (freqByteData[i] > magnitude) {
                magnitude = freqByteData[i];
            }
        }
        analyserContext.fillStyle = "#777777";
        if (magnitude > 230) {
            analyserContext.fillStyle = "#AA7777";
        }
        analyserContext.fillRect(0, canvasHeight, canvasWidth, -(logvalue(magnitude, canvasHeight)));
        // Draw rectangle for each frequency bin.
        /*for (var i = 0; i < numBars; ++i) {
            var magnitude = 0;
            var offset = Math.floor( i * multiplier );
            // gotta sum/average the block, or we miss narrow-bandwidth spikes
            for (var j = 0; j< multiplier; j++)
                magnitude += freqByteData[offset + j];
            magnitude = magnitude / multiplier;
            //var magnitude2 = freqByteData[i * multiplier];
            analyserContext.fillStyle = "#777777";
            analyserContext.fillRect(i * SPACING, canvasHeight, BAR_WIDTH, -magnitude);
        }*/
    }
    
    rafID = window.requestAnimationFrame( updateAnalysers );
}

function gotStream(stream) {
    inputPoint = audioContext.createGain();

    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;
    audioInput.connect(inputPoint);

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect( analyserNode );
    audioRecorder = new Recorder( inputPoint );

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect( zeroGain );
    zeroGain.connect( audioContext.destination );
    updateAnalysers();
}

function initAudio() {
        if (!navigator.getUserMedia)
            navigator.getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
        if (!navigator.cancelAnimationFrame)
            navigator.cancelAnimationFrame = navigator.webkitCancelAnimationFrame || navigator.mozCancelAnimationFrame;
        if (!navigator.requestAnimationFrame)
            navigator.requestAnimationFrame = navigator.webkitRequestAnimationFrame || navigator.mozRequestAnimationFrame;

    navigator.getUserMedia(
        {
            "audio": {
                "mandatory": {
                    "googEchoCancellation": "false",
                    "googAutoGainControl": "false",
                    "googNoiseSuppression": "false",
                    "googHighpassFilter": "false"
                },
                "optional": []
            },
        }, gotStream, function(e) {
            alert('Error getting audio');
            console.log(e);
        });
}

window.addEventListener('load', initAudio );

function isInt(value) {
  if (isNaN(value)) {
    return false;
  }
  var x = parseFloat(value);
  return (x | 0) === x;
}

function startMetronome(ci=0, as=0) {
    var preroll = false;
    var autostop = false;
    var autostop_start = false;
    if (ci > 0) {
        preroll = true;
    }
    if (as > 0) {
        autostop = true;
    }
    bpm = $("#bpm").val();
    if (isInt(bpm)) {
        if (bpm > 500) {
            $("#bpm").val(500);
            bpm = 500;
        } else if (bpm < 1) {
            $("#bpm").val(1);
            bpm = 1;
        }
    } else {
        $("#bpm").val(120);
        bpm = 120;
    }
    subdivision = $("#subdivision").val();

    if (isInt(subdivision)) {
        if (subdivision < 1) {
            $("#subdivision").val(1);
            subdivision = 1;
        } else if (subdivision > 100) {
            $("#subdivision").val(100);
            subdivision = 100;
        }
    } else {
        $("#subdivision").val(4);
        subdivision = 4;
    }
    
    var ci_beats = subdivision * ci;
    var as_beats = subdivision * as;

    var timing = 60000/bpm;

    if (!m_on) {
        $("#play_symbol").hide();
        $("#pause_symbol").show();
        num_clicks = 0;
        m_on = true;
        up.pause();
        up.currentTime = 0;
        up.play();
        num_clicks++;
        m = setInterval(function() {
            
            if (preroll) {
                if (ci_beats > 1) {
                    ci_beats--;
                } else {
                    toggleRecording();
                    preroll = false;
                    if (autostop) {
                        autostop_start = true;
                    }
                }
            }
            
            if (autostop_start) {
                if (as_beats > 1) {
                    as_beats--;
                } else {
                    toggleRecording();
                    autostop = false;
                    autostop_start = false;
                }
            }
            
            if (num_clicks % subdivision == 0) {
                up.pause();
                up.currentTime = 0;
                up.play();
            } else {
                down.pause();
                down.currentTime = 0;
                down.play();
            }
            num_clicks++;
            
        }, timing);
    } else {
        $("#pause_symbol").hide();
        $("#play_symbol").show();

        clearInterval(m);
        m_on = false;
    }
}

$(document).ready(function() {
    
    $('#record_button').click(function() {
        if (!ci || recording) {
            toggleRecording();
        } else if (ci && as) {
            var cim_setting = $("#cim_setting").val();
            var as_setting = $("#as_setting").val();
            startMetronome(cim_setting, as_setting);
        } else {
            var cim_setting = $("#cim_setting").val();
            startMetronome(cim_setting);
        }
    });
    
    $('#m_button').click(function() {
        startMetronome();
    });
    
    $('#mr_checkbox').click(function() {
        if (!mr) {
            $(this).css({
                "background-color": "black"
            });
            mr = true;
        } else {
            $(this).css({
                "background-color": "none"
            });
            mr = false;
        }
    });
    $('#ci_checkbox').click(function() {
        if (!ci) {
            $(this).css({
                "background-color": "bisque"
            });
            ci = true;
        } else {
            $(this).css({
                "background-color": "rgba(0,0,0,0)"
            });
            ci = false;
        }
    });
    $('#as_checkbox').click(function() {
        if (!as) {
            $(this).css({
                "background-color": "bisque"
            });
            as = true;
        } else {
            $(this).css({
                "background-color": "rgba(0,0,0,0)"
            });
            as = false;
        }
    });
});