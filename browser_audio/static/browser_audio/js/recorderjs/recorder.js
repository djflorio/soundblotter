/*License (MIT)

Copyright Â© 2013 Matt Diamond

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and 
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
*/
$(document).ready(function() {
    
    audiojs.events.ready(function() {
        var as = audiojs.createAll();
    });
    
    // Path to the "worker" code, which is code that is run on a separate thread
    // than the main thread.
    var WORKER_PATH = js_worker;

    // Create a function expression called Recorder.
    var Recorder = function(source, cfg){
      // Set config to the value of cfg if it exists, or
      // to an empty array if it doesn't.
      var config = cfg || {};
      // Set bufferLen to bufferLen from config if it exists, or
      // to 4096 if it doesn't.
      var bufferLen = config.bufferLen || 4096;
      // Set the context of this instance of Recorder to the context from
      // the source array.
      this.context = source.context;

      // Use either createJavaScriptNode or createScriptProcessor to create
      // a script processor node used for audio processing. Basically, this will
      // use createJavaScriptNode if the browser does not support the newer
      // createScriptProcessor.
      if(!this.context.createScriptProcessor){
         this.node = this.context.createJavaScriptNode(bufferLen, 2, 2);
      } else {
        // Create an audio script processor, setting the buffer size, number of
        // input channels, and number of output channels, and assign it to
        // the node variable for this instance of Recorder.
         this.node = this.context.createScriptProcessor(bufferLen, 2, 2);
      }

      // Create a new Worker, which is an object that runs the specified code
      // (in this case, the code in recorderWorker.js) on a separate thread from
      // the main thread. This makes for better performance on the main thread.
      
    var worker = new Worker(config.workerPath || WORKER_PATH);
        worker.onerror = function(event){
            throw new Error(event.message + " (" + event.filename + ":" + event.lineno + ")");
        };
      // Send the message 'init' to the worker, and provide a config array that
      // has the sample rate. The 'onMessage' method on the worker's end contains
      // a switch statement, which calls certain methods based on the message it
      // receives. In this case, it calls the init method.
      worker.postMessage({
        command: 'init',
        config: {
          sampleRate: this.context.sampleRate
        }
      });
      // Define recording as false, and then define currCallback.
      // This is shorthand for var recording = false; var currCallback;
      var recording = false,
        currCallback;
      // This gets called every time the node experiences an audio process event.
      // The rate at which this event is fired depends on the buffer length.
      this.node.onaudioprocess = function(e){
        if (!recording) return;
        // If recording is set to true, send a message to the worker to fire the
        // record method, passing in the buffer values as parameters.
        worker.postMessage({
          command: 'record',
          buffer: [
            e.inputBuffer.getChannelData(0),
            e.inputBuffer.getChannelData(1)
          ]
        });
      }
      // Method that updates a property to the config variable for this instance
      // of Recorder.
      this.configure = function(cfg){
        for (var prop in cfg){
          if (cfg.hasOwnProperty(prop)){
            config[prop] = cfg[prop];
          }
        }
      }
      // Method that sets the recording variable to true, effectively starting
      // the recording process.
      this.record = function(){
        recording = true;
      }
      // Method that sets the recording variable to false, effectively stopping
      // the recording process.
      this.stop = function(){
        recording = false;
      }
      // Method that sends a 'clear' message to the worker, which resets the
      // recording.
      this.clear = function(){
        worker.postMessage({ command: 'clear' });
      }
      // Method that sends a 'getBuffers' message to the worker. Not too sure what
      // it's for yet, but it gets called once a recording is ended.
      this.getBuffers = function(cb) {
        currCallback = cb || config.callback;
        worker.postMessage({ command: 'getBuffers' })
      }
      // Method that sends a 'exportWAV' message to the worker. Gets called once
      // recording has ended.
      this.exportWAV = function(cb, type){
        currCallback = cb || config.callback;
        type = type || config.type || 'audio/wav';
        if (!currCallback) throw new Error('Callback not set');
        worker.postMessage({
          command: 'exportWAV',
          type: type
        });
      }
      // Same as above, only mono.
      this.exportMonoWAV = function(cb, type){
        currCallback = cb || config.callback;
        type = type || config.type || 'audio/wav';
        if (!currCallback) throw new Error('Callback not set');
        worker.postMessage({
          command: 'exportMonoWAV',
          type: type
        });
      }
      // This is called when a message is received from the worker. Here, we are
      // using the data from e, and passing it into a callback method. At this point,
      // the callback method is 'doneEncoding(blob)' from main.js.
      worker.onmessage = function(e){
        var blob = e.data;
        currCallback(blob);
      }
      // ????????
      source.connect(this.node);
      this.node.connect(this.context.destination);   // if the script node is not connected to an output the "onaudioprocess" event is not triggered in chrome.
    };
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    $("body").on('click', '.rename-button', function() {
        var c = "";
        audio_id = $(this).attr('data_title_id');
        title_area = document.getElementById(audio_id);
        current_title = $(this).attr('data_current_title');
        c += '<form action="/audio/rename_audio/" method="post">';
        c += '<input type="text" id="audio_rename" name="audio_name" value="';
        c += current_title;
        c += '"><input type="submit" value="save" id="submit_rename" class="audio-link">';
        c += ' | <div class="cancel-button audio-link" data_current_title="';
        c += current_title;
        c += '" data_title_id="';
        c += audio_id;
        c += '">cancel</div>';
        title_area.innerHTML = c;
    });
    
    $("body").on('click', '.cancel-button', function() {
        var c = ""
        console.log("cancel");
        audio_id = $(this).attr('data_title_id');
        title_area = document.getElementById(audio_id);
        current_title = $(this).attr('data_current_title');
        
        c += current_title;
        c += " | <a class='rename-button audio-link' data_title_id='";
        c += audio_id;
        c += "' data_current_title='";
        c += current_title;
        c += "'>rename</a>";
        
        title_area.innerHTML = c;
    });

    Recorder.setupDownload = function(blob, filename){
        var csrftoken = getCookie('csrftoken');
        var url = (window.URL || window.webkitURL).createObjectURL(blob);
        //var link = document.getElementById("save");
        var playarea = document.getElementById("playarea");
        //link.href = url;
        //link.download = filename || 'output.wav';
      
        var data = new FormData();
        data.append('file', blob);
        
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        
      
      $.ajax({
        type: 'POST',
        url: '/audio/create_file/',
        data: data,
        contentType: false,
        processData: false,
        success: function(r) {
            
          location.reload();
        },
        error: function(r) {
          console.log(r);
        }
      });
      
      
    }

    window.Recorder = Recorder;
});