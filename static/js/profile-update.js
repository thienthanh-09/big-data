$(function () {
    handleImageUpload();
});

function handleImageUpload(){
    document.getElementById('id_avatar').onchange = function (el){
        let files = el.target.files;

        if (files[0].size / 1024 / 1024 > 10){
            showToast(gettext('Image size should be less than 10MB'), 'danger');
            el.target.value = '';
        }
    }
}