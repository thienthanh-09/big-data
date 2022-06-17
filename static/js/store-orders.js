import {csrfHeader} from './utils.js';
$(function () {
    handleAccept();
    handleReject();
});

function handleAccept(){
    $('.accept-btn').click(function () {
        let orderId = $(this).attr('order-id');
        post(orderId, 'Accepted');
    });
}

function handleReject(){
    $('.reject-btn').click(function () {
        let orderId = $(this).attr('order-id');
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
        complete: function (data){
            window.location.reload();
        }
    });
}

