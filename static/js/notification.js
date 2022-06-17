import {csrfHeader} from './utils.js';
$(function () {
    handleNotificationClick();
    handleMarkAllAsRead();
    handleHideReadNotification();
    handleUnhideReadNotification();
});

function handleUnhideReadNotification(){
    $('#unhide-read-noti').click(function(){
        window.location.href = '/notification/?hide_read=false';
    })
}

function handleHideReadNotification(){
    $('#hide-read-noti').click(function(){
        window.location.href = '/notification/?hide_read=true';
    })
}

function handleMarkAllAsRead(){
    $('#mark-all-read-btn').click(function(){
        $.ajax({
            type: "post",
            url: "read-all/",
            headers: csrfHeader(),
            dataType: "json",
            complete: function(data){
                if (data.status == 204){
                    window.location.reload();
                }
            }
        });
    });
}

function handleNotificationClick(){
    $('.notification').click(function(){
        let notificationId = $(this).attr('item-id');
        if ($(this).hasClass('opacity-25')){
            directToNotification($(this).find('a'));
            return;
        }
        markAsRead(this, notificationId);
    });
}

function directToNotification(noti){
    // noti[0].click();
}

function markAsRead(noti, id){
    $.ajax({
        type: "post",
        url: `read/${id}/`,
        headers: csrfHeader(),
        dataType: "json",
        complete: function(data){
            if (data.status == 204){
                directToNotification($(noti).find('a'));
                $(noti).addClass(['opacity-25']);
            }
        }
    });
}