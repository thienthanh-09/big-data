import {csrfHeader, showToast, increaseCartNumber} from './utils.js';

export function addToCart(itemId, quantity){
    $.ajax({
        type: "post",
        url: "/cart/",
        headers: csrfHeader(),
        data: {
            'item_id': itemId,
            'quantity': quantity,
        }, 
        success: function (response) {
            showToast(gettext('Added to cart'));
        },
        error: function (response) {
            showToast(response.responseText, 'danger');
        },
    });
}

export function removeFromCart(detailId){
    $.ajax({
        type: "delete",
        url: `/cart/detail/${detailId}/`,
        headers: csrfHeader(),
        success: function(data, textStatus, jqXHR){
            window.location.reload();
        },
    });
}

$(function () {
    handleRemoveItem();
    handleCheckout();
    handleEditQuantity();
});

function handleEditQuantity(){
    $('.item-quantity').click(function(){
        $(this).hide();
        $(this).siblings('.item-quantity-edit').prop('hidden', false);
    });

    $('.item-quantity-edit-confirm').click(function(){
        let detailId = $(this).attr('detail-id');
        let quantity = $(this).siblings('.item-quantity-edit-value').val();
        $.ajax({
            type: "patch",
            url: "/cart/detail/" + detailId + "/",
            headers: csrfHeader(),
            data: {
                'quantity': quantity,
            },
            dataType: "dataType",
            success: function (response) {
                window.location.reload();
            },
            error: function (response) {
                showToast(response.responseText, 'danger');
            },
        });
    });
}

function handleRemoveItem(){
    $('.remove-item-btn').click(function(){
        let detailId = $(this).attr('detail-id');
        removeFromCart(detailId);
    })
}

function handleCheckout(){
    $('.purchase-btn').click(function(){
        let cartId = $(this).attr('cart-id');
        checkout(cartId);
    })
}

function checkout(cartId){
    window.location.href = `/checkout/${cartId}/`;
}