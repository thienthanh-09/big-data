import {csrfHeader, showToast} from './utils.js';
$(function () {
    handleDeliveryAddress();
    handlePaymentMethodClick();
    handlePurchaseBtnClick();
});

function handleDeliveryAddress(){
    $('#check-me').change(function () {
        if ($(this).is(':checked')) {
            $('#delivery-address').prop('hidden', true);
            $('#my-address').prop('hidden', false);
        }
    });
    $('#check-other').change(function () { 
        if (this.checked){
            $('#delivery-address').prop('hidden', false);
            $('#my-address').prop('hidden', true);
        }
    });
}

function handlePaymentMethodClick(){
    $('.payment-method').click(function(){
        console.log('click');
        for (let i = 0; i < 3; i++){
            $('.payment-method').eq(i).removeClass('bg-primary');
            $('.payment-method-content').eq(i).prop('hidden', true);
        }
        $(this).addClass('bg-primary');
        let index = $(this).parent().index();
        $('.payment-method-content').eq(index).prop('hidden', false);
        $('.purchase-btn').prop('hidden', false);
    });
}

function handlePurchaseBtnClick(){
    $('.purchase-btn').click(function(){
        let orderId = $(this).attr('order-id'),
            address;
        if ($('#check-me').is(':checked')){
            address = $('#my-address').val();
        } else {
            address = $('#delivery-address').val();
        }
        if (address == ''){
            showToast(gettext('Delivery address cannot be empty'), 'danger');
            return;
        }
        purchase(orderId, address);
    });
}

function purchase(orderId, address){
    $.ajax({
        type: "post",
        url: `/checkout/${orderId}/`,
        headers: csrfHeader(),
        data: {
            'address': address
        },
        dataType: "json",
        success: function (response) {
            window.location.href = '/thank-you/'
        },
        error: function (response){
            showToast(response.responseText, 'danger');
        }
    });
}