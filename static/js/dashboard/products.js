import {csrfHeader, showToast} from '../utils.js';

$(function () {
    handleDeleteProduct();
    handleSales();
    handleAddQuantity();
});

function handleAddQuantity(){
    let trans = {
        add_success: gettext('Quantity added successfully'),
        add_fail: gettext('Error adding quantity'),
        validate_fail: gettext('Invalid quantity'),
        prompt_title: gettext('Enter quantity'),
    };

    const addQuantity = (id, quantity) => {
        $.ajax({
            type: "post",
            url: `/me/store/product/quantity/${id}/`,
            headers: csrfHeader(),
            data: {
                quantity: quantity,
            },
            success: function (data, textStatus, jqXHR) {
                showToast(trans.add_success);
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            },
            error: function (){
                showToast(trans.add_fail, 'danger');
            }
        });
    };

    $('.add-quantity').click(function(){
        let productId = $(this).parent().data('id');
        let quantity = prompt(trans.prompt_title, '0');
        if (quantity == null){
            return;
        }
        if (!isNaN(quantity)){
            quantity = parseInt(quantity);
            if (quantity > 0){
                addQuantity(productId, quantity);
            } else {
                showToast(trans.validate_fail, 'danger');
            }
        } else {
            showToast(trans.validate_fail, 'danger');
        }
    });
}

function handleDeleteProduct(){
    $('.delete-product-btn').click(function(){
        let opt = confirm(gettext('Are you sure you want to delete this product?'));
        if (!opt){
            return;
        }
        let productId = $(this).parent().parent().data('id');
        $.ajax({
            type: "post",
            url: `/me/store/product/remove/${productId}/`,
            headers: csrfHeader(),
            success: function (response) {
                window.location.reload();
            },
        });
    });
}

function handleSales(){
    const changePrice = () => {
        let value = $('#sale-value').val();
        if (value == ''){
            value = 0;
        }
        let newPrice;
        if ($('.sale-choice').eq(1).prop('checked')){
            newPrice = parseFloat($('#original-price').text()) - parseFloat(value);
        } else {
            newPrice = parseFloat($('#original-price').text()) * (1 - parseFloat(value) / 100);
        }

        $('#sale-price').text(Math.floor(newPrice));
    };

    $('.modal-body').on('click', '.sale-choice', function(){
        let index = $(this).parent().index();
        if (this.checked){
            $('.sale-choice').eq(1 - index).prop('checked', false);
            $('#sale-value-symbol').text(index == 0 ? '%' : '$');
        } else {
            $('.sale-choice').eq(1 - index).prop('checked', true);
            $('#sale-value-symbol').text(index == 1 ? '%' : '$');
        }
        changePrice();
    });
    let modal;
    $('.sales-btn').click(function(){
        let productId = $(this).parent().parent().data('id');
        $.ajax({
            type: "get",
            url: `/render/sale/${productId}`,
            success: function (response) {
                $('.modal-body').html(response);
                $('#quick-modal').modal('show');
            }
        });
    });

    $('.modal-body').on('keyup', '#sale-value', function(){
        changePrice();
    });

    $('.modal-body').on('click', '#sale-confirm-btn', function(){
        let productId = $(this).data('id');
        let value = $('#sale-value').val();
        if (value == ''){
            value = 0;
        }
        $.ajax({
            type: "post",
            url: `/me/store/product/sale/${productId}/`,
            headers: csrfHeader(),
            data: {
                value: value,
                type: $('.sale-choice').eq(0).prop('checked') ? 'percentage' : 'fixed',
                duration: $('#sale-duration').val(),
            },
            dataType: "text",
            success: function (data, textStatus, jqXHR) {
                showToast(gettext('Sale added successfully'));
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            },
            error: function (){
                showToast(gettext('Error adding sale'), 'danger');
            }
        });
    });

    $('.modal-body').on('click', '#sale-remove-btn', function(){
        let productId = $(this).data('id');
        $.ajax({
            type: "delete",
            url: `/me/store/product/sale/${productId}/`,
            headers: csrfHeader(),
            success: function (data, textStatus, jqXHR) {
                showToast(gettext('Sale removed successfully'));
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            },
            error: function (){
                showToast(gettext('Error removing sale'), 'danger');
            }
        });
    });
}