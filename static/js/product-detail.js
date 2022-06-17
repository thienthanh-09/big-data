import {addToCart} from './cart.js';
import { csrfHeader, showToast, showImageViewer } from './utils.js';

$(function () {
    handleAddToCart();
    handleComment();
    handleRating();
    handleShareProduct();
    handleStartChat();
    handleLikeProduct();
    handleImageView();
    handleFixedAddCart();
    handleTimeCountDown();
});

function handleTimeCountDown(){
    let time = Date.parse($('#time-countdown').data('expired'));
    const numberToIcon = (number) => {
        let response = '<span class="number-frame rounded">';
        number = number.toString();
        for (let i = 0; i < number.length; i++){
            response += `<i class="number text-light fa fa-${number[i]}"></i>`;
        }
        response += '</span>';
        return response;
    };

    const updateTime = () => {
        let diff = time - Date.now();
        let seconds = Math.floor((diff / 1000) % 60),
            minutes = Math.floor((diff / 1000 / 60) % 60),
            hours = Math.floor((diff / (1000 * 60 * 60)) % 24),
            days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (seconds < 10){
            seconds = '0' + seconds;
        }
        if (minutes < 10){
            minutes = '0' + minutes;
        }
        if (hours < 10){
            hours = '0' + hours;
        }

        let time_text = `${numberToIcon(days)}${numberToIcon(hours)} ${numberToIcon(minutes)} ${numberToIcon(seconds)}`;
        $('#time-countdown').html(time_text);
    }
    setInterval(() => {
        updateTime();
    }, 1000);
}

function handleFixedAddCart(){
    let offset = $('#add-cart-div').offset().top + $('#add-cart-div').height();
    $(window).scroll(function(){
        let scroll = $(window).scrollTop();
        if (scroll > offset){
            $('#fixed-cart').css('visibility', 'visible');
            $('#fixed-cart').css('opacity', '1');
        } else {
            $('#fixed-cart').css('visibility', 'invisible');
            $('#fixed-cart').css('opacity', '0');
        }
    });
}

function handleImageView(){
    $('.product-img').click(function(){
        let url = $(this).attr('src');
        showImageViewer(url);
    });
}

function handleLikeProduct(){
    let like_text = gettext('Remove from Favorited products'),
        unlike_text = gettext('Add to Favorited products');
    const likeProduct = (btn, productId) => {
        $.ajax({
            type: "post",
            url: `/like/${productId}/`,
            headers: csrfHeader(),
            dataType: "json",
            success: function (response) {
                showToast(response.message);
                $(btn).find('.fa').addClass('fa-heart');
                $(btn).find('.fa').removeClass('fa-heart-o');
                $(btn).addClass('text-danger');
                $('#fav_text').text(like_text);
            }
        })
    };
    const unlikeProduct = (btn, productId) => {
        $.ajax({
            type: "delete",
            url: `/like/${productId}/`,
            headers: csrfHeader(),
            dataType: "json",
            success: function (response) {
                showToast(response.message);
                $(btn).find('.fa').removeClass('fa-heart');
                $(btn).find('.fa').addClass('fa-heart-o');
                $(btn).removeClass('text-danger');
                $('#fav_text').text(unlike_text);
            }
        })
    };

    $('#like-product-btn').click(function(){
        let like = $(this).hasClass('text-danger');
        let productId = $(this).attr('product-id');
        if (!like){
            likeProduct(this, productId);
        } else {
            unlikeProduct(this, productId);
        }
    });
}

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

function handleShareProduct(){
    $('#share-url-btn').click(function(){
        let url = window.location.href;
        navigator.clipboard.writeText(url).then(function() {
            showToast(gettext('Link copied to clipboard'));
        }, function (){
            showToast(gettext('Link copy failed'), 'danger');
        });
    });

    $('#share-fb-btn').attr('href', 'https://www.facebook.com/sharer/sharer.php?u=' + window.location.href);
}

let user_rate = 3;
function handleRating(){
    $('.rating-star').hover(function () {
            let rate = $(this).index();
            changeRateView(rate);
        }, function () {
            changeRateView(user_rate);
        }
    );

    $('.rating-star').click(function () {
        let rate = $(this).index();
        user_rate = rate;
        changeRateView(user_rate);
    });
}

function changeRateView(rate){
    for (let i = 0; i <= rate; i++) {
        $('.rating-star').eq(i).removeClass('fa-regular').addClass('fa-solid');
    }
    for (let i = rate + 1; i < 5; i++) {
        $('.rating-star').eq(i).removeClass('fa-solid').addClass('fa-regular');
    }
}

function handleAddToCart(){
    const handleAdjustQuantity = () => {
        $('.increase-qty-btn').on('click', function () {
            let qty = parseInt($(this).parent().find('.qty-input').val());
            qty++;
            $('.qty-input').val(qty);
        });
        $('.decrease-qty-btn').on('click', function () {
            let qty = parseInt($(this).parent().find('.qty-input').val());
            if (qty > 1){
                qty--;
                $('.qty-input').val(qty);
            }
        });
    };

    handleAdjustQuantity();
    $('.add-cart').click(function(){
        let qty = parseInt($('.qty-input').val());
        let id = $(this).attr('item-id');
        addToCart(id, qty);
    });
}

function handleComment(){
    $('#write-review-btn').click(function(){
        if ($('#review-session').prop('hidden')){
            $('#review-session').prop('hidden', false);
        } else {
            $('#review-session').prop('hidden', true);
        }
    });
    
    $('#comment-btn').click(function(){
        let commentInput = $('#comment-input').val(),
            productId = $(this).attr('product-id');
        if (commentInput.length > 0){
            comment(commentInput, productId);
        }
    });
}

function comment(commentInput, productId){
    $.ajax({
        url: `/comment/${productId}/`,
        method: 'POST',
        headers: csrfHeader(),
        data: {
            rate: user_rate + 1,
            content: commentInput
        },
        success: function(data){
            window.location.reload();
        },
        error: function(data){
            showToast(data.responseText, 'danger');
        }
    });
}