import {showToast} from './utils.js';

$(function () {
    handleImageUpload();
    handleRemoveImage();
    handleRemoveVideo();
});

function handleRemoveVideo(){
    $('.remove-video-btn').click(function () {
        let id = $(this).attr('data-id');
        $(`div[data-video-id=${id}]`).remove();
        $('form').append(`<input type="hidden" name="removed_videos" value="${id}">`);
    });
}

function handleRemoveImage(){
    $('.product-image').click(function () {
        let id = $(this).attr('data-id');
        $(`div[data-image-id=${id}]`).remove();
        $('form').append(`<input type="hidden" name="removed_images" value="${id}">`);
    });
}

function handleImageUpload(){
    $('.image-size-validate').change(function (el) {
        let files = el.target.files;
        for (let i = 0; i < files.length; i++){
            let file = files[i];
            if (file.size / 1024 / 1024 > 10){
                showToast(gettext('File size should be less than 10MB'), 'danger');
                el.target.value = '';
            }
        };
    });
}