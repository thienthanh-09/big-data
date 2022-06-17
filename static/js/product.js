import {showToast} from './utils.js';

$(function () {
    selectChosenFilter();
    handleSelectSort();
    handleSelectFilter();
    handleAutoComplete();
});

function handleAutoComplete(){
    $('#search-input').change(function (e) { 
        $('#submit-btn').click();
    });
    $('#search-input').keyup(function(){
        let pattern = $(this).val();
        $.ajax({
            type: "get",
            url: "/product/",
            data: {
                search: pattern,
            },
            dataType: "json",
            success: function (response) {
                let productList = $('#product-list');
                productList.empty();
                response.forEach(function (item) {
                    let productItem = `<option value="${item.name}">${item.price} USD</option>`;
                    productList.append(productItem);
                });
            }
        });
    });
}

function selectChosenFilter(){
    let val = $('#select-sort').attr('selected-item');
    $('#select-sort').val(val);
    $('#f-rate').val($('#h-rate').val());
    $('#f-category').val($('#h-category').val());
    $('#f-from').val($('#h-from').val());
    $('#f-to').val($('#h-to').val());
    if ($('#h-show').val() == 'on'){
        $('#f-show').prop('checked', true);
    }
}

function handleSelectSort(){
    $('#select-sort').change(function(){
        let sortBy = $(this).val();
        $('#h-sort').val(sortBy);
        $('#form-search').submit();
    });
}

function handleSelectFilter(){
    let modal;
    $('#filter-btn').click(function(){
        modal = new bootstrap.Modal($('#filter-modal'));
        modal.show();
    });

    $('#filter-confirm-btn').click(function(){
        if ($('#f-category').val() != '-1' ) {
            $('#h-category').val($('#f-category').val());
        } else {
            $('#h-category').val('');
        }
        if (parseInt($('#f-from').val()) > parseInt($('#f-to').val()) || parseInt($('#f-from').val()) < 0 || parseInt($('#f-to').val()) < 0) {
            showToast(gettext('Price range is invalid'), 'danger');
            return;
        }

        $('#h-rate').val($('#f-rate').val());
        $('#h-from').val($('#f-from').val());
        $('#h-to').val($('#f-to').val());
        $('#h-show').val($('#f-show').val());
        if ($('#f-show').prop('checked')){
            $('#h-show').val('on');
        } else {
            $('#h-show').val('off');
        }
        $('#form-search').submit();
    });
}