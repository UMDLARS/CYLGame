'use strict';

let DEBUGGING = false;

class Player {
  constructor(parent_div, height, width, draw_func, show_btn_bar = false, show_debug_table = false, show_progress_bar = false) {
    parent_div = $(parent_div);
    this.parent_div = parent_div;
    this.show_btn_bar = show_btn_bar;
    this.show_debug_table = show_debug_table;
    this.show_progress_bar = show_progress_bar;
    this.draw_func = draw_func;

    // Player state
    this.is_playing = false;
    this.cur_frame = 0;
    this.real_cur_frame = 0;
    this.fps = 10;
    this.playback_timeout = 1000 / this.fps;
    this.is_really_playing = false;
    this.replay_vars = [];
    this.replay_frames = [];
    this.reset_speed();

    // Create canvas
    this.canvas = $("<canvas>");
    this.canvas.attr("height", height + "px");
    this.canvas.attr("width", width +"px");
    this.parent_div.append(this.canvas);


    if (this.show_progress_bar) {
      // Create Progress bar
      let bar_parent = $("<div>");
      let bar = $("<div>");
      this.playback_progress_bar = $("<input>");
      this.playback_progress_bar.attr("id", "progressBar");
      this.playback_progress_bar.attr("type", "range");
      this.playback_progress_bar.attr("min", "0");
      this.playback_progress_bar.attr("max", "0");
      this.playback_progress_bar.attr("step", "1");
      this.playback_progress_bar.css("width", "100%");
      this.playback_progress_bar.on("input", () => this.on_progress_input());
      bar.append(this.playback_progress_bar);
      bar_parent.append(bar);
      this.playback_progress_bar_text = $("<span>");
      this.playback_progress_bar_text.text("Frame 0 of 0");
      bar_parent.append(this.playback_progress_bar_text);
      this.seed_text = $("<span>");
      this.seed_text.css("float", "right");
      bar_parent.append(this.seed_text);
      this.code_hash_text = $("<span>");
      this.code_hash_text.css("float", "right");
      this.code_hash_text.css("padding-right", "1em");
      bar_parent.append(this.code_hash_text);
      this.parent_div.append(bar_parent);
      this.parent_div.append($("<br>"));
    }

    if (this.show_btn_bar) {
      // Create btn bar
      this.btn_bar = $("<div>").addClass("btnBar");
      // Stop btn
      this.btn_bar.append($("<button>")
        .text("Stop")
        .click(() => {
          this.on_stop_click();
        }));
      // Slower btn
      this.btn_bar.append($("<button>")
        .text("<<")
        .click(() => {
          this.on_slower_click();
        }));
      // Prev btn
      this.btn_bar.append($("<button>")
        .text("<")
        .click(() => {
          this.on_prev_click();
        }));
      // toggle btn
      this.btn_bar.append($("<button>")
        .text("Play/Pause")
        .click(() => {
          this.on_toggle_play_click();
        }));
      // next btn
      this.btn_bar.append($("<button>")
        .text(">")
        .click(() => {
          this.on_next_click();
        }));
      // faster btn
      this.btn_bar.append($("<button>")
        .text(">>")
        .click(() => {
          this.on_faster_click();
        }));
      this.btn_bar.append($("<button>")
        .text(">|")
        .click(() => {
          this.on_end_click();
        }));
      if (this.show_debug_table) {
        // Set seed and toggle debug table:
        this.debug_toggle_btn = $("<button>")
          .text("Show Debug Table")
          .click(() => {
            this.on_toggle_debug_table_click();
          });
        this.btn_bar.append($("<div>").css("float", "right")
          .append($("<button>")
            .text("Set Map Seed")
            .click(() => {
              set_seed();  // This is a hack. Fix me sometime.
            }))
          .append(this.debug_toggle_btn)
          .append($("<button>")
          .text("Export GIF")
          .click(() => {
            this.export_gif();
          })));
      }
      this.btn_bar.append($("<br>"));
      this.parent_div.append(this.btn_bar);
      this.disable_btn_bar();
    }

    if (this.show_debug_table) {
      // Create debug table
      this.debug_table = $("<table>").css("display", "none").addClass("debugTable");
      this.parent_div.append($("<div>").append($("<br>")).append($("<center>").append(this.debug_table)));
    }

    // <!--<div id="btn-bar">-->
    //     <!--<button onclick="stop();">Stop</button>-->
    //     <!--<button onclick="slower();">&lt;&lt;</button>-->
    //     <!--<button onclick="prevFrame();">&lt;</button>-->
    //     <!--<button onclick="toggle_play();">Play/Pause</button>-->
    //     <!--<button onclick="nextFrame();">&gt;</button>-->
    //     <!--<button onclick="faster();">&gt;&gt;</button>-->
    //     <!--<div style="float: right;">-->
    //         <!--<button id="btnSetSeed" onclick="set_seed();">Set Map Seed</button>-->
    //         <!--<button id="btnToggleDebug" onclick="toggle_debug_table();">Show Debug Table</button>-->
    //     <!--</div>-->
    //     <!--<br>-->
    // <!--</div>-->
    // <!--<div>-->
    //     <!--<br>-->
    //     <!--<center>-->
    //         <!--<table id="debugTable" style="display: none;">-->
    //         <!--</table>-->
    //     <!--</center>-->
    // <!--</div>-->
  }

  load_from_tokens(gtoken, utoken, callback) {
    this.debug_table.html("");
    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + 'game/' + gtoken + "/" + utoken,
      dataType: "json",
      success: (data) => {
        if (window.canceled) {
          return;
        }
        callback();
        if (data["error"]) {
          alert(data["error"]);
        } else {
          this.drawFrames(data["screen"], data["player"]["debug_vars"]);
          this.setSeed(data["seed"]);
          this.setCodeHash(data["player"]["code_hash"]);
          this.enable_btn_bar();
        }
      },
      failure: (errMsg) => {
        if (window.canceled) {
          return;
        }
        callback();
        // hideLoading();
        alert(errMsg);
      }
    });
    return false;
  }

  // Button bar handlers
  on_stop_click() {
    this.stop();
  }

  on_slower_click() {
    if (this.cur_frame >= this.replay_frames.length - 1) {
      this.on_prev_click();
    }
    if (this.cur_speed > 0) {
      this.reset_speed();
      this.cur_speed *= -1;
    }
    this.cur_speed *= 2;
    this.play();
  }

  on_faster_click() {
    if (this.cur_speed < 0) {
      this.reset_speed();
    }
    this.cur_speed *= 2;
    this.play();
  }

  on_prev_click() {
    this.pause();
    if (this.cur_frame > 0) {
      this.cur_frame--;
      this.real_cur_frame = this.cur_frame;
    }
    this.reset_speed();
    this.drawCurFrame();
  }

  on_next_click() {
    this.pause();
    if (this.cur_frame < this.replay_frames.length - 1) {
      this.cur_frame++;
      this.real_cur_frame = this.cur_frame;
    }
    this.reset_speed();
    this.drawCurFrame();
  }

  on_toggle_play_click() {
    this.reset_speed();
    if (this.is_playing) {
      this.pause();
    } else {
      this.play();
    }
  }

  on_end_click() {
    this.end();
  }

  on_progress_input() {
    this.pause();
    this.reset_speed();
    this.cur_frame = parseInt(this.playback_progress_bar.prop("value"), 10);
    this.real_cur_frame = this.cur_frame;
    this.drawCurFrame();
  }

  export_gif(){
    this.pause();
    // show_loading();
    let f = 0;
    let f_start = parseInt(prompt("What frame would you like to start at?"));
    let f_end = parseInt(prompt("What frame would you like to end at?"));
    let images = [];
    let canvas = $('canvas').get(1);
    for (f = f_start; f < f_end; f++) {
      this.cur_frame = this.real_cur_frame = f;
      this.drawCurFrame();
      let blob = canvas.toDataURL();
      //images.push(canvas.toDataURL("image/png"));

      //Get data from canvas
      let img = document.createElement("img");
      img.src = canvas.toDataURL('image/png');
      images.push(img);
    }
    gifshot.createGIF({
      'images': images,
      'gifWidth': canvas.width,
      'gifHeight': canvas.height,
    },function(obj) {
      // hide_loading();
      if(!obj.error) {
        //var image = obj.image,
        //animatedImage = document.createElement('img');
        //animatedImage.src = image;
        //document.body.appendChild(animatedImage);

        // Download the image
        let a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        // // The next two steps may be redundant?
        // let blob = new Blob(obj.image, {type: "octet/stream"});
        // let url = window.URL.createObjectURL(blob);
        a.href = obj.image;
        a.download = "cyl.gif";
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert(`There was an error: ${object.error}`);
      }
    });
  }

  stop() {
    this.pause();
    this.reset_speed();
    this.cur_frame = 0;
    this.real_cur_frame = 0;
    this.drawCurFrame();
  }

  pause() {
    this.is_playing = false;
  }

  play() {
    this.is_playing = true;
    if (this.is_really_playing == false) {
      if (this.cur_frame >= this.replay_frames.length - 1) {
        this.cur_frame = 0;
        this.real_cur_frame = 0;
      }
      this.startDrawLoop();
    }
  }

  end() {
    this.pause();
    this.reset_speed();
    this.cur_frame = this.replay_frames.length - 1;
    this.real_cur_frame = this.cur_frame;
    this.drawCurFrame();
  }

  // Debug table toggle
  on_toggle_debug_table_click() {
    if (this.debug_table.css("display") == "none") {
      this.debug_table.css("display", "");
      this.debug_toggle_btn.html("Hide Debug Table");
    } else {
      this.debug_table.css("display", "none");
      this.debug_toggle_btn.html("Show Debug Table");
    }
  }

  // Button Bar stuff
  disable_btn_bar() {
    this.btn_bar.find("button").attr("disabled", true);
  }

  enable_btn_bar() {
    this.btn_bar.find("button").attr("disabled", false);
  }

  reset_speed() {
    this.cur_speed = 0.5;
  }

  drawFrames(frames, vars) {
    this.stop();
    this.replay_frames = frames;
    this.replay_vars = vars;
    this.playback_progress_bar.prop({"min": 1, "max": this.replay_frames.length});
    this.play();
  }

  startDrawLoop() {
    this.last_frame_time = 0;
    requestAnimationFrame((t) => {this.drawLoop(t);});
  }

  reqLoop() {
    requestAnimationFrame((t) => {this.drawLoop(t);});
  }

  drawLoop(now) {
    if (this.is_playing) {
      if (!this.last_frame_time) {
        this.last_frame_time = now;
      }
      let time_delta = now - this.last_frame_time;
      if (time_delta < this.playback_timeout) {
        this.reqLoop();
        return;
      }
      this.real_cur_frame += this.cur_speed * (time_delta / 1000);
      let old_cur_frame = this.cur_frame;
      this.cur_frame = Math.min(Math.floor(this.real_cur_frame), this.replay_vars.length - 1);
      this.cur_frame = Math.max(this.cur_frame, 0);
      if (old_cur_frame == this.cur_frame) {
        this.reqLoop();
        return;
      }
      if (this.cur_frame < this.replay_frames.length && this.cur_frame > -1) {
        this.drawCurFrame();
        if (this.cur_frame == this.replay_vars.length - 1 && this.cur_speed > 0) {
          this.pause();
        } else if (this.cur_frame == 0 && this.cur_speed < 0) {
          this.pause();
        }
      } else {
        this.pause();
      }
      this.is_really_playing = true;
      if (DEBUGGING) {
        if (!this.ave_draw_time) {
          this.ave_draw_time = (performance.now() - now) / time_delta;
          this.ave_draw_time_n = 1;
        } else {
          this.ave_draw_time_n += 1;
          this.ave_draw_time = ((this.ave_draw_time * (this.ave_draw_time_n - 1)) / this.ave_draw_time_n) + (((performance.now() - now) / time_delta) / this.ave_draw_time_n);
        }
        console.log("Ave percent of time drawing: " + this.ave_draw_time + "%");
      }
      this.last_frame_time = now;
      this.reqLoop();
    } else {
      this.is_really_playing = false;
    }
  }

  drawCurFrame() {
    if (this.cur_frame >= 0 && this.cur_frame < this.replay_frames.length) {
      this.playback_progress_bar.prop("value", this.cur_frame);
      this.playback_progress_bar_text.html("Frame " + this.cur_frame + " of " + (this.replay_frames.length));
      this.draw_func(this.canvas[0], this.replay_frames[this.cur_frame]);
      if (this.show_debug_table) {
        this.create_var_table(this.replay_vars[this.cur_frame]);
      }
    } else {
      console.log("Not drawing frame: " + this.cur_frame);
    }
  }

  setSeed(seed) {
    this.seed_text.html("Map: " + seed);
  }

  setCodeHash(code_hash) {
    this.code_hash_text.html("Code: " + code_hash.substring(0,8));
  }

  create_var_table(vars) {
    let keys = Object.keys(vars);
    keys.sort();

    let row = $("<tr>").append($("<th>").html("Name")).append($("<th>").html("Value"));
    this.debug_table.html("").append(row);
    keys.forEach((item, index) => {
        let value = this.var_to_string(vars[item]);
        let row = $("<tr>").append($("<td>").html(item)).append($("<td>")
            .text(value));
        this.debug_table.append(row);
    });
  }

  var_to_string(value) {
    if (Array.isArray(value)) {
      return "[" + value.map((val) => {return this.var_to_string(val);}).join(",") + "]"
    }
    return value.toString();
  }
}

class InteractivePlayer extends Player {
  constructor(...args) {
    super(...args);

    this.state = {};
    this.ready = true;

    $(document).keypress((event) => {
      if (this.canvas.is(':visible')) {
        this.move(event.originalEvent.key);
      }
    });
    this.move('');
  }

  move(key) {
    if (this.ready) {
      this.ready = false;
      console.log(this.state);
      this.load_from_moves_and_state(key, function () {});
    } else {
      console.log('Player waiting for response');
    }
  }

  load_from_moves_and_state(move, callback) {
    if (this.show_debug_table) {
      this.debug_table.html("");
    }
    console.log("Requesting with " + JSON.stringify({move: move, state: this.state}));
    $.ajax({
      type: "POST",
      url: $SCRIPT_ROOT + 'play',
      data: JSON.stringify({move: move, state: this.state}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: (data) => {
        if (window.canceled) {
          return;
        }
        callback();
        if (data["error"]) {
          alert(data["error"]);
        } else {
          this.state = data["state"];
          this.frame = data["frame"];
          this.draw_func(this.canvas[0], this.frame);
          function playAgain()
          {
             playMore.disabled = true;
             this.ready = true;
             this.state = {};
             this.move('');
          }
          var playMore = document.getElementById("playAgain");
          playMore.onclick = playAgain.bind(this,playMore);
          if (data["lost"]) {
              playMore.disabled = false;
          } else {
            this.ready = true;
          }
        }
      },
      failure: (errMsg) => {
        if (window.canceled) {
          return;
        }
        callback();
        // hideLoading();
        alert(errMsg);
      }
    });
    return false;
  }
}
