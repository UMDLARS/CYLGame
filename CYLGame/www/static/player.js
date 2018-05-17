'use strict';

let DEBUGGING = false;

class Player {
  constructor(parent_div, height, width, draw_func, show_btn_bar = false, show_debug_table = false) {
    parent_div = $(parent_div);
    this.parent_div = parent_div;
    this.show_btn_bar = show_btn_bar;
    this.show_debug_table = show_debug_table;
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

    // Create Progress bar
    let bar_parent = $("<div>");
    let bar = $("<div>");
    bar.addClass("progress");
    this.playback_progress_bar = $("<div>");
    this.playback_progress_bar.addClass("progress-bar");
    this.playback_progress_bar.addClass("fast");
    this.playback_progress_bar.attr("role", "progressbar");
    this.playback_progress_bar.attr("aria-valuemin", "0");
    this.playback_progress_bar.attr("aria-valuemax", "100");
    this.playback_progress_bar.css("width", "100%");
    bar.append(this.playback_progress_bar);
    bar_parent.append(bar);
    this.playback_progress_bar_text = $("<span>");
    this.playback_progress_bar_text.text("Frame 0 of 0");
    bar_parent.append(this.playback_progress_bar_text);
    this.seed_text = $("<span>");
    this.seed_text.css("float", "right");
    bar_parent.append(this.seed_text);
    this.parent_div.append(bar_parent);
    this.parent_div.append($("<br>"));

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
          .append(this.debug_toggle_btn
          ));
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
          this.drawFrames(data["screen"], data["player"]);
          this.setSeed(data["seed"]);
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
      this.playback_progress_bar.css("width", (this.cur_frame / (this.replay_frames.length - 1)) * 100 + "%");
      this.playback_progress_bar_text.html("Frame " + (this.cur_frame + 1) + " of " + (this.replay_frames.length));
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

  create_var_table(vars) {
    let keys = Object.keys(vars);
    keys.sort();

    let row = $("<tr>").append($("<th>").html("Name")).append($("<th>").html("Value"));
    this.debug_table.html("").append(row);
    keys.forEach((item, index) => {
        let row = $("<tr>").append($("<td>").html(item)).append($("<td>").html(vars[item]));
        this.debug_table.append(row);
    });
  }
}