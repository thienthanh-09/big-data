import './utils.js';
import { csrfHeader, showToast } from './utils.js';
$(function () {
    handleChangeEmail();
});

function handleChangeEmail(){
    $('.edit-btn').click(function(){
        $('#non-edit').prop('hidden', true);
        $('#edit').prop('hidden', false);
    })

    $('#email-input').keydown(function (e) { 
        if (e.keyCode == 13) {
            changeEmail();
        }
    });
}

function changeEmail(){
    $.ajax({
        type: "post",
        headers: csrfHeader(),
        data: {
            'email': $('#email-input').val(),
        },
        success: function (response) {
            window.location.reload();
        },
        error: function (response) {
            showToast(response.responseText, 'danger');
        }
    });
}