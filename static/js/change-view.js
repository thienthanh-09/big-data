$(function () {
    handleChangeViewMode();
});

function handleChangeViewMode(){
    $('.view-mode-btn').click(function(){
        let viewMode = $(this).attr('view-mode');
        let index = $(this).index();
        $('.view-mode-btn').eq(1 - index).removeClass('btn-primary');
        $('.view-mode-btn').eq(1 - index).addClass('btn-outline-primary');
        $(this).addClass('btn-primary');
        $(this).removeClass('btn-outline-primary');
        if (viewMode == 'list'){
            $('.product-list-mode').prop('hidden', false);
            $('.product-grid-mode').prop('hidden', true);
        } else {
            $('.product-list-mode').prop('hidden', true);
            $('.product-grid-mode').prop('hidden', false);
        }
    });
}