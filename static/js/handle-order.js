import {csrfHeader} from './utils.js';
$(function () {
    handleAccept();
    handleReject();
});

function handleAccept(){
    $('#accept-btn').click(function () {
        let orderId = $(this).parent().data('id');
        post(orderId, 'Accepted');
    });
}

function handleReject(){
    $('#reject-btn').click(function () {
        let orderId = $(this).parent().data('id');
        post(orderId, 'Rejected');
    });
}

function post(orderId, result){
    $.ajax({
        type: "post",
        headers: csrfHeader(),
        url: `/me/store/orders/`,
        data: {
            'id': orderId,
            'result': result,
        },
        dataType: "json",
        success: function (data){
            window.location.href = data.next;
        }
    });
}

