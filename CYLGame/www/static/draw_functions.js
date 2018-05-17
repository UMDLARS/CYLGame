// helper function
function torgba(color, alpha) {
    var r = parseInt(color.substring(1,3), 16);
    var g = parseInt(color.substring(3,5), 16);
    var b = parseInt(color.substring(5,7), 16);

   return "rgba(" + r + "," + g + "," + b + "," + alpha + ")";
}

var draw_char = function(canvas, ctx, args){
   	var img=document.getElementById("chars");
	var char = args[0];
	var x = args[1];
	var y = args[2];
	var char_height = args[3];
	var char_width = args[4];
    var rows = 16;
    var cols = 16;

    if (window.charSetLayout == "col") {
        var sourceY = (char%rows)*char_width;
        var sourceX = Math.floor(char/rows)*char_width;
        var sourceWidth = char_width;
        var sourceHeight = char_height;
    } else if (window.charSetLayout == "row") {
        var sourceX = (char%cols)*char_width;
        var sourceY = Math.floor(char/cols)*char_width;
        var sourceWidth = char_width;
        var sourceHeight = char_height;
    }

    var destWidth = sourceWidth;
    var destHeight = sourceHeight;
    var destX = x*char_width;
    var destY = y*char_height;

    ctx.drawImage(img, sourceX, sourceY, sourceWidth, sourceHeight, destX, destY, destWidth, destHeight);
};

var draw_tank = function(canvas, ctx, args) {
	var x = args[0];
	var y = args[1];
	var rotation = args[2];
	var turret = args[3];
	var fire = args[4];
	var led = args[5];
	var color = args[6];

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rotation);
 
    ctx.fillStyle = color;
    ctx.fillRect(-5, -4, 10, 8);
    ctx.fillStyle = "#777";
    ctx.fillRect(-7, -9, 15, 5);
    ctx.fillRect(-7,  4, 15, 5);
    ctx.rotate(turret);
    if (fire) {
    	ctx.fillStyle = ("rgba(255,255,64," + fire/5 + ")");
    	ctx.fillRect(0, -1, 45, 2);
    } else {
        if (led) {
            ctx.fillStyle = "#f00";
        } else {
            ctx.fillStyle = "#000";
        }
        ctx.fillRect(0, -1, 10, 2);
    }
 
    ctx.restore();
};

var draw_sensors = function(canvas, ctx, args) {
	var x = args[0];
	var y = args[1];
	var rotation = args[2];
	var turret = args[3];
	var color = args[4];
	var sensors = args[5];
	// [radius, rotation, width, turret, triggered]
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rotation);

    ctx.lineWidth = 1;
	var sensorStroke = torgba(color, 0.4);
    for (var i = 0; i < sensors.length; i++) {
		if (sensors[i][0] ==  0) {
			// sensor does not exist
			continue;
		}
        var s = new Array(4);
		var angle = sensors[i]["angle"];
		var width = sensors[i]["width"];
		s[0] = sensors[i]["range"];
		s[1] = angle - width/2;
		s[2] = angle + width/2;
		s[3] = sensors[i]["turret"] ? 1 : 0;
        var adj = turret * s[3];

        if (sensors[i]["triggered"] != 0) {
            // Sensor is triggered
            ctx.strokeStyle = "#000";
        } else {
            ctx.strokeStyle = sensorStroke;
        }
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, s[0], s[1] + adj, s[2] + adj, false);
        ctx.closePath();
        ctx.stroke();
    }

    ctx.restore();
};

var draw_crater = function(canvas, ctx, args) {
    var points = 7;
    var angle = Math.PI / points;

	var x = args[0];
	var y = args[1];
	var rotation = args[2];
	var color = args[3];

	var craterStroke = torgba(color, 0.5);
	var craterFill = torgba(color, 0.2);

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rotation);

    ctx.lineWidth = 2;
    ctx.strokeStyle = craterStroke;
    ctx.fillStyle = craterFill;
    ctx.beginPath();
    ctx.moveTo(12, 0);
    for (i = 0; i < points; i += 1) {
        ctx.rotate(angle);
        ctx.lineTo(6, 0);
        ctx.rotate(angle);
        ctx.lineTo(12, 0);
    }
    ctx.closePath()
    ctx.stroke();
    ctx.fill();

    ctx.restore();
};

var draw_functions = {
	"char" : draw_char,
	"tank" : draw_tank,
	"sensors" : draw_sensors,
	"crater" : draw_crater
};
