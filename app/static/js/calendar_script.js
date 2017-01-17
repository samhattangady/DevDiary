var canvas = document.getElementById('calendar');
var ctx = canvas.getContext('2d');

function draw(calendar_data) {
    var width = canvas.width;
    var height = canvas.height;

    /*
        Comments on math required.
        divide width into number of months
        within each month tab, 20% top for text
        find number of columns using rows and number of items
        use smaller of height/rows,width/column as dimension
        find x and y buffers to center the other dimension
        use 1/6 as margin for each day -> get side of square
        render squares per month
    */
    var months = calendar_data.months.length;
    var month_width = width / months;
    var top_text_buffer = height *.2;
    var columns = calendar_data.days[0].length / calendar_data.rows;
    var sqr_side = Math.min(height*.8 / calendar_data.rows, width / columns);
    var x_buffer = (month_width - sqr_side*columns) / 2;
    var y_buffer = (height - sqr_side*calendar_data.rows) / 2;
    var sqr_dim = sqr_side * 5/6;
    var colour = '#FFFFFF'

    var font_size = Math.ceil(top_text_buffer * .8);
    ctx.font = font_size.toString() + 'px Architects Daughter';

    for (i=0; i<calendar_data.months.length; i++) {
        ctx.fillStyle = calendar_data.missed_day;
        ctx.fillText(calendar_data.months[i],((month_width*i)+month_width/4), top_text_buffer*.8)
        for (j=0; j<calendar_data.days[i].length; j++) {
            // -1 should give a dull square, 1 a bright square
            if (calendar_data.days[i][j] < 0) {
                colour = calendar_data.missed_day;
            } else if (calendar_data.days[i][j] > 0) {
                colour = calendar_data.colours[i];
            } else {
                continue;
            }
            ctx.fillStyle = colour;
            single_day((month_width*i) + (x_buffer + (sqr_side * (j%columns))),
                     (top_text_buffer + (sqr_side*(Math.floor(j/columns)))),
                     sqr_dim, sqr_dim, colour);
        }
    }
}

function single_day(x, y, width, height, colour) {
    ctx.fillStyle = colour;
    ctx.fillRect(x, y, width, height);
    ctx.fill();
}
