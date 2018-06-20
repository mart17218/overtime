function checkInput(target_input) {
    for (var i = 0; i < $(target_input).length; i++) {
        if ($(target_input + ':eq(' + i + ')').val().length == 0) return false;
    }
    return true;
}
function searchPreList(target_tbody, target_overlay, target_btn, username, password) {
    isLoading(true, target_overlay, target_btn);
    $('#result_list tbody tr').remove();

    var user_data = { username: username, password: password };
    $.ajax({
        url: "/pre_ot_list",
        type: 'POST',
        contentType:"application/json; charset=utf-8",
        data: JSON.stringify(user_data)
    }).done(function(data, textStatus, jqXHR) {
        var tr_str = '';

        if(!data || data.length === 0) {
            tr_str = '<tr><td>暫無查詢結果</td></tr>';
        } else {
            $.each(data, function(key, val) {
                tr_str += '<tr>' + '<td>' + val.date + '</td><td>' + val.method + '</td><td><div class="status-light ' + (val.status === '\u5df2\u751f\u6548' ? 'done' : 'pending') + '">' + val.status + '</div></td></tr>';
            });
        }
        $(target_tbody).html(tr_str);
    }).fail(function() {
        // show error msg
    }).always(function() {
        isLoading(false, target_overlay, target_btn);
    });
}
function searchActList(target_tbody, target_overlay, target_btn, username, password) {
    isLoading(true, target_overlay, target_btn);
    $('#result_list tbody tr td').remove();

    var user_data = { username: username, password: password };
    $.ajax({
        url: "/ot_list",
        type: 'POST',
        contentType:"application/json; charset=utf-8",
        data: JSON.stringify(user_data)
    }).done(function(data, textStatus, jqXHR) {
        var tr_str = '';

        if(!data || data.length === 0) {
            tr_str = '<tr><td>暫無查詢結果</td></tr>';
        } else {
            $.each(data, function(key, val) {
                tr_str += '<tr>' + '<td>' + val.date + '</td><td>' + val.method + '</td><td><div class="status-light ' + (val.status === '\u5df2\u751f\u6548' ? 'done' : 'pending') + '">' + val.status + '</div></td></tr>';
            });
        }
        $(target_tbody).html(tr_str);
    }).fail(function() {
        // show error msg
    }).always(function() {
        isLoading(false, target_overlay, target_btn);
    });
}
function applyPreOt(target_overlay, target_btn, status_div, post_data) {
    isLoading(true, target_overlay, target_btn);
    $.ajax({
        url: "/pre",
        type: 'POST',
        contentType:"application/json; charset=utf-8",
        data: JSON.stringify(post_data)
    }).done(function(data, textStatus, jqXHR) {
        $(status_div).addClass('done').text('預報成功');
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $(status_div).addClass('fail').text('預報失敗(' + jqXHR.responseText + ')');
    }).always(function() {
        isLoading(false, target_overlay, target_btn);
        $('#search_pre').trigger('click');
    });
}
function applyActOt(target_overlay, target_btn, status_div, post_data) {
    isLoading(true, target_overlay, target_btn);
    $.ajax({
        url: "/ot",
        type: 'POST',
        contentType:"application/json; charset=utf-8",
        data: JSON.stringify(post_data)
    }).done(function(data, textStatus, jqXHR) {
        $(status_div).addClass('done').text('實報成功');
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $(status_div).addClass('fail').text('實報失敗(' + jqXHR.responseText + ')');
    }).always(function() {
        isLoading(false, target_overlay, target_btn);
        $('#search_act').trigger('click');
    });
}
// @TODO
function searchWorkTimeList(post_data) {
    $.ajax({
        url: "/abnormal_list",
        type: 'POST',
        contentType:"application/json; charset=utf-8",
        data: JSON.stringify(post_data)
    }).done(function(data, textStatus, jqXHR) {
        console.log('done', data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.log('fail');
    }).always(function() {
    });
}
function isLoading(flag, target_overlay, target_btn) {
    if(flag) {
        $(target_overlay).removeClass('hide');
        $(target_btn).addClass('disable-click');
    } else {
        $(target_overlay).addClass('hide');
        $(target_btn).removeClass('disable-click');
    }
}
function getPoem() {
    var target_input = '#pre_form input[name="pre-reason"]';
    $.ajax({
        url: "/sentence",
        type: 'GET',
        contentType:"application/json; charset=utf-8"
    }).done(function(sentence, textStatus, jqXHR) {
        $(target_input).attr('placeholder', sentence);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $(target_input).attr('placeholder', jqXHR.responseText);
    });
}
function getUser(post_data, target_btn) {
    isLoading(true, '', target_btn);
    var name_target = '.welcome .user';
    $.ajax({
        url: "/get_user",
        type: 'POST',
        contentType:"application/json; charset=utf-8",
        data: JSON.stringify(post_data)
    }).done(function(data, textStatus, jqXHR) {
        $(name_target).text(data.USER_NAME);
        $('.float-mouse').data('acc', post_data.username);
        $('.float-mouse').data('pw', post_data.password);
        $('section.login-page').addClass('hide');
        $('section.main-page').removeClass('hide');
    }).fail(function(jqXHR, textStatus, errorThrown) {
        var animate_effect = ['bounce', 'hinge', 'tada'],
            random_effect = animate_effect[new Date().getSeconds() % (animate_effect.length)];
        $('.envelope .content .main-figure').removeClass().addClass('main-figure animated infinite ' + random_effect);
    }).always(function() {
        isLoading(false, '', target_btn);
    });
}