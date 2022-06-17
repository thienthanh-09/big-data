import {csrfHeader, showToast} from './utils.js';

$(function () {
    handleStartChat();
});

function handleStartChat(){
    let text = {
        error: gettext('Login to start chat with store'),
    }
    $('#start-chat-btn').click(function(){
        let storeId = $(this).attr('data-store');
        $.ajax({
            type: "post",
            url: "/chat/start/",
            headers: csrfHeader(),
            data: {
                store_id: storeId
            },
            dataType: "json",
            success: function (response) {
                window.location.href = '/chat/';
            },
            error: function (response) {
                showToast(text.error, 'danger');
            }
        });
    });
}