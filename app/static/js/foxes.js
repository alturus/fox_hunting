var status = 0;
var timer_id;
var seconds;
var current_field_id = 0;


function seconds_to_clock(seconds) {
    var clock = '';
    var hours = 0;
    var minutes = 0;
    if (seconds > 3599) {
        hours = Math.trunc(seconds / 3600);
        seconds = seconds % 3600;
    }
    if (seconds > 59) {
        minutes = Math.trunc(seconds / 60);
        seconds = seconds % 60;
    }
    seconds = Math.trunc(seconds);
    if (hours < 10) hours = '0' + String(hours)
    if (minutes < 10) minutes = '0' + String(minutes)
    if (seconds < 10) seconds = '0' + String(seconds)
    if (hours == '00') {
        clock = minutes + ':' + seconds;
    } else {
        clock = hours + ':' + minutes + ':' + seconds;
    }
    return clock;
}


function update_timer(seconds) {
    $('#timer').text(seconds_to_clock(seconds));
}


function start_timer() {
    seconds = 0;
    timer_id = setInterval(function() {
        current_timer = Number($('#timer').text());
        seconds++;
        update_timer(seconds);
    }, 1000);
}


function stop_timer() {
    clearInterval(timer_id);
}


function set_current_field_id(id) {
    var req = $.ajax({
        'url': '/current_field_id/' + id
    });
    req.done(function(id) {
         current_field_id = id;
         window.location = '/';
    });
}


function update_fields_menu() {
    var req = $.ajax({
        'url': '/fields'
    });
    req.done(function(fields) {
        var fields_menu = $('#fields-menu');
        for(var id in fields) {
            var item = $('<a />', {
                'class': 'dropdown-item',
                'href': '#',
                'data-value': id,
                'text': fields[id]
            });
            item.on('click', function(evt) {
                current_field_id = $(this).attr('data-value');
                if (window.location.pathname != '/') {
                    evt.preventDefault();
                    set_current_field_id(current_field_id);
                    //window.location = '/';
                } else {
                    init_game();
                }
            });
            fields_menu.append(item);
        }
    });
}


function update_top_10(field_id) {
    var req = $.ajax({
        'url': '/records/' + field_id
    });
    req.done(function(records) {
        var top_10_table = $('#top-10 tbody');
        $('#top-10_title').text('TOP 10 (' + records[0].size + ')');
        top_10_table.find('tr').remove();
        var number = 1;
        records.forEach(function(record) {
            var row = $('<tr />');
            row.append($('<td />', {'text': number}));
            if (record.isYou) {
                var td = $('<td />', {'text': record.player + ' '});
                td.append($('<span />', {
                    'class': 'badge badge-light bg-blue',
                    'text': 'You'
                }));
                row.append(td);
            } else {
                row.append($('<td />', {'text': record.player}));
            }
            row.append($('<td />', {'class': 'text-center', 'text': record.shot_count}));
            row.append($('<td />', {'class': 'text-right', 'text': seconds_to_clock(record.seconds)}));
            top_10_table.append(row);
            number++;
        });
    });
}


function shot(cell) {
    var x, y;
    var cell_id = cell.attr('id');
    if (cell_id) {
        var cell_position = cell_id.split('-', 2);
        x = cell_position[0] - 1;
        y = cell_position[1] - 1;
    }

    if (status == 2) {
        // The game is already finished, don't shoot please!
        return;
    }

    var req = $.ajax({
        'url': '/shot/' + x + '/' + y
    });
    req.done(function(data) {
        if (status == 0) {
            status = 1;
            start_timer();
        }
        //status = 1;
        var td = cell.parent();
        if (data.last_shot_result == 'hit') {
            var img = $('<img />' , {
                'src': 'static/img/fox_40.png',
                'alt': '',
                'style': 'height: 40px; weight: 40px'
            });
            cell.remove();
            td.append(img);
            $('#fox_count').text(data.fox_count - data.hits);
            if (data.status == 2) {
                // Game over
                status = 2;
                stop_timer();
                if (data.is_in_top_10) {
                    $('#message').html("<strong>GAME OVER <br>Congratulations! You are in TOP 10!</strong>");
                } else {
                    $('#message').html("<strong>GAME OVER <br>You've found all foxes!</strong>");
                }
                $('#play_again').fadeIn('slow');
                update_top_10(current_field_id);
            }
        } else {
            var opened_cell = $('<a />', {
                'id': String(x+1) + '-' + String(y+1),
                'class': 'btn btn-outline-dark disabled opened',
                'href': '#',
                'html': '&nbsp;'
            });
            opened_cell.text(data.last_shot_result);
            cell.remove();
            td.append(opened_cell);
        }
        $('#shot_count').text(data.shot_count);
    });
}


function genField(id) {
    var req = $.ajax({
        'url': '/field/' + id
    });
    req.done(function(state) {
        var field_size = state.field_size;
        var fox_count = state.fox_count;
        var shot_count = state.shot_count;
        $('#fox_count').text(fox_count)
        $('#shot_count').text(shot_count)
        var field = $('#field')
        field.find('tr').remove();
        for(var y=0; y < field_size; y++) {
            var row = $('<tr />');
            for(var x=0; x < field_size; x++) {
                var button = $('<a />', {
                    'id': String(x+1) + '-' + String(y+1),
                    'class': 'btn btn-success bg-green',
                    'href': '#',
                    'html': '&nbsp;'
                });
                var column = $('<td />');
                column.append(button)
                row.append(column)
                button.on('click', function(evt){
                    evt.preventDefault();
                    if ($(this).attr('class') != 'opened') {
                        shot($(this));
                    }
                });
            }
            field.append(row)
        }
    });
}


function init_game() {
    status = 0;
    stop_timer();
    update_timer(0);
    $('#play_again').hide();
    $('#message').html('');
    genField(current_field_id);
    update_top_10(current_field_id);
}


$(function(){
    $('[data-toggle="popover"]').popover({
        placement: 'auto',
        trigger: 'hover',
        html: true
    });
    update_fields_menu();
    init_game();

    $('#play_again').on('click', function(){
        init_game();
    });

    $('.navbar-brand').on('click', function(evt){
        if (window.location.pathname != '/') {
            evt.preventDefault();
            window.location = '/';
        } else {
            init_game();
        }
    });
});
