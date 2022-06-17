import {csrfHeader, showToast} from './utils.js';

$(function () {
    getQueryData();
    handleRemoveProduct();
    handleSearch();
    handleSort();
    handleSales();
});

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

        $('#sale-price').text(Math.ceil(newPrice));
    };

    $('.sale-choice').click(function(){
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
        let id = $(this).attr('item-id'),
            name = $(this).attr('item-name'),
            price = $(this).attr('item-price');
        $('#sale-confirm-btn').attr('item-id', id);
        $('#sale-remove-btn').attr('item-id', id);
        modal = new bootstrap.Modal($('#staticBackdrop'));
        $('#modal-product-name').text(name);
        $('#original-price').text(price);
        $.ajax({
            type: "get",
            url: `/me/store/product/sale/${id}/`,
            success: function (response) {
                $('#sale-value').val(response.value);
                if (response.type == 'P'){
                    $('.sale-choice').eq(0).prop('checked', true);
                    $('#sale-value-symbol').text('%');
                } else {
                    $('.sale-choice').eq(1).prop('checked', true);
                    $('#sale-value-symbol').text('$');
                }
                changePrice();
                modal.show();
            },
            error: function (response){
                $('#sale-value').val(0);
                $('.sale-choice').prop('checked', false);
                $('.sale-choice').eq(0).prop('checked', true);
                changePrice();
                modal.show();
            }
        });
    });

    $('#sale-value').keyup(function(){
        changePrice();
    });

    $('#sale-confirm-btn').click(function(){
        let value = $('#sale-value').val();
        if (value == ''){
            value = 0;
        }
        $.ajax({
            type: "post",
            url: `product/sale/${$(this).attr('item-id')}/`,
            headers: csrfHeader(),
            data: {
                value: value,
                type: $('.sale-choice').eq(0).prop('checked') ? 'percentage' : 'fixed',
                duration: $('#sale-duration').val(),
            },
            dataType: "text",
            success: function (data, textStatus, jqXHR) {
                showToast(gettext('Sale added successfully'));
                modal.hide();
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            },
            error: function (){
                showToast(gettext('Error adding sale'), 'danger');
            }
        });
    });

    $('#sale-remove-btn').click(function(){
        $.ajax({
            type: "delete",
            url: `/me/store/product/sale/${$(this).attr('item-id')}/`,
            headers: csrfHeader(),
            success: function (data, textStatus, jqXHR) {
                showToast(gettext('Sale removed successfully'));
                modal.hide();
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

let queryData = {
    search: '',
    sort_by: 'id',
}

function getQueryData(){
    let search = getUrlParam('search');
    if (search){
        queryData.search = search;
        $('#search-input').val(search);
    }
    let sortBy = getUrlParam('sort_by');
    if (sortBy){
        queryData.sort_by = sortBy;
    }
}

function getUrlParam(name){
    let url_string = window.location.href;
    let url = new URL(url_string);
    return url.searchParams.get(name);
}

function handleSort(){
    $('.sort-attr').click(function(){
        let sortBy = $(this).attr('field');
        if (sortBy == queryData.sort_by){
            sortBy = '-' + sortBy;
        }
        queryData.sort_by = sortBy;
        window.location.href = '?' + $.param(queryData);
    });
}

function handleSearch(){
    $('#search-input').keyup(function(e){
        e.which == 13 && $('#search-btn').click();
    });
    $('#search-btn').click(function(){
        var query = $('#search-input').val();
        queryData.search = query;
        window.location.href = '?' + $.param(queryData);
    });
}

function handleRemoveProduct(){
    $('.remove-product-btn').click(function(){
        let productId = $(this).attr('product-id');
        removeProduct(productId);
    });
}

function removeProduct(productId){
    $.ajax({
        type: "post",
        url: `product/remove/${productId}/`,
        headers: csrfHeader(),
        success: function (response) {
            window.location.reload();
        },
    });
}