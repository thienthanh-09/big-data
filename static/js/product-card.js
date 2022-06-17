import {csrfHeader, showToast} from './utils.js';
import {addToCart} from './cart.js';

$(function () {
    handleViewProductDetail();
    handleQuickAddToCart(); 
    handleLikeProduct();
    handleQuickView();
});

function handleQuickView(){
    const handleAdjustQuantity = () => {
        $('.modal-body').on('click', '.increase-qty-btn', function () {
            let qty = parseInt($(this).parent().find('.qty-input').val());
            qty++;
            $(this).parent().find('.qty-input').val(qty);
        });
        $('.modal-body').on('click', '.decrease-qty-btn', function () {
            let qty = parseInt($(this).parent().find('.qty-input').val());
            if (qty > 1){
                qty--;
                $(this).parent().find('.qty-input').val(qty);
            }
        });
    };

    const handleAddToCart = () => {
        $('.modal-body').on('click', '#quick-view-add-cart', function () {
            let qty = parseInt($('.qty-input').val());
            let id = $('#quick-view-add-cart').attr('product-id');
            addToCart(id, qty);
        });
    };

    handleAdjustQuantity();
    handleAddToCart();
    $('.view-product-btn').click(function(){
        $.ajax({
            type: "get",
            url: `/render/quickview/${$(this).attr('product-id')}/`,
            success: function (response) {
                $('.modal-body').html(response);
                $('#quick-modal').modal('show');
            }
        });
    });
}

function handleLikeProduct(){
    const likeProduct = (btn, productId) => {
        $.ajax({
            type: "post",
            url: `/like/${productId}/`,
            headers: csrfHeader(),
            dataType: "json",
            success: function (response) {
                $(btn).data('fav', 'True');
                $(btn).html('<i class="fa fa-heart text-danger" aria-hidden="true"></i>');
                showToast(response.message);
            },
            error: function (response) {
                showToast(gettext('You need to login to like this product'), 'danger');
            },
        })
    };
    const unlikeProduct = (btn, productId) => {
        $.ajax({
            type: "delete",
            url: `/like/${productId}/`,
            headers: csrfHeader(),
            dataType: "json",
            success: function (response) {
                $(btn).data('fav', 'False');
                $(btn).html('<i class="fa fa-heart-o" aria-hidden="true"></i>');
                showToast(response.message);
            }
        })
    };

    $('.like-product-btn').click(function(){
        let isFavorited = $(this).data('fav');
        if (isFavorited == 'False'){
            likeProduct(this, $(this).attr('product-id'));
        } else {
            unlikeProduct(this, $(this).attr('product-id'));
        }
    });
}

function handleQuickAddToCart(){
    $('.add-to-cart-btn').click(function(){
        let id = $(this).attr('product-id');
        $.ajax({
            type: "post",
            url: "/cart/",
            headers: csrfHeader(),
            data: {
                'item_id': id,
                'quantity': 1,
            }, 
            success: function (response) {
                $.ajax({
                    type: "get",
                    url: `/render/quickadd/${id}/`,
                    success: function(response){
                        $('.modal-body').html(response);
                        $('#quick-modal').modal('show');
                    }
                });
            },
            error: function (response) {
                showToast(response.responseText, 'danger');
            },
        });
        
    });
}

function handleViewProductDetail(){
    $('.product-name,.card-img-top').click(function(){
        let itemURL = $(this).parent().parent().attr('item-url');
        window.location.href = itemURL;
    });
}