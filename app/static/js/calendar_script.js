var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');

function draw(calendar_data) {
    var width = canvas.width;
    var height = canvas.height;
    ctx.font = "48px san-serif";
    ctx.fillText(calendar_data.months[0], 10, 50);
    console.log(calendar_data.days[0].length)
    console.log(canvas.width)
}