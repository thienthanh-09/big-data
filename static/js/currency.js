$(function () {
    const update_currency = () => {
        $.ajax({
            url: '/currency/',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                window.rate = JSON.parse(data).USD_VND;
                $('.price-hover').each(function (index, element) {
                    $(element).attr('data-toggle', 'tooltip');
                    $(element).attr('data-placement', 'top');
                    let price = $(element).attr('item-value');
                    $(element).attr('title', '$' + price + ' = ' + (price * window.rate).toLocaleString() + ' VND');
                    $(element).css('z-index', '2');
                });
            }
        });
    }
    update_currency();
    setInterval(update_currency, 1000 * 60 * 15);
});