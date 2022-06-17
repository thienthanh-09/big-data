import {csrfHeader, showToast, showImageViewer} from './utils.js';
$(function () {
    handleSelectRole();
    handleSearch();
    handleSelectDestinator();
    handleSendMessage();
    handleSendImage();
    loadEmoji();
    handleImageView();
});

function handleImageView(){
    $('.messages').on('click', '.msg', function () {
        let image = $(this).attr('src');
        showImageViewer(image);
    });
}

function handleSendImage(){
    $('#image-btn').click(function () {
        $('#image-input').click();
    });

    $('#image-input').change(function () {
        let file = $('#image-input')[0].files[0];
        if (file == undefined) return;
        if (file.size / 1024 / 1024 > 10){
            showToast(gettext('File size should be less than 10MB'), 'danger');
            return;
        }
        let formData = new FormData();
        formData.append('image', file);
        formData.append('role', window.role);
        formData.append('id', window.destination_id);

        $.ajax({
            type: "post",
            url: "/chat/message/",
            headers: csrfHeader(),
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                let msgId = response.id;

                window.chatSocket.send(JSON.stringify({
                    'message': '',
                    'message_id': msgId,
                }));
            }
        });
    });
}

function loadEmoji(){
    Emoji.setDataUrl('/emoji/all.json');
    Emoji.load();
    let emojiList = Emoji.get();
    emojiList.forEach(emoji => {
        let url = Emoji.get(emoji);
        $('.emoji-list').append(`
            <img src="${url}" alt="${emoji}" title="${emoji}" class="emoji emoji-ctrl" height="30px">
        `);
    });

    $('img.emoji-ctrl').hover(function () {
        $(this).addClass('bg-primary');     
    }, function () {
        $(this).removeClass('bg-primary');
    });

    $('.emoji-ctrl').click(function () {
        let emoji = $(this).attr('alt');
        let text = $('#chat-input').val();
        $('#chat-input').val(`${text}:${emoji}:`);
    });
}

function handleSendMessage(){
    const sendMessage = () => {
        let message = $('#chat-input').val();
        if (message.length > 0){
            window.chatSocket.send(JSON.stringify({
                'message': message,
            }));
            $('#chat-input').val('');
        }
    }
    $('#chat-input').keyup(function (e) {
        if (e.keyCode == 13){
            sendMessage();
        }
    });

    $('#send-button').click(function () {
        sendMessage();
    });
}

function handleSelectDestinator(){
    disableChatController();
    let clickedFormat = ['bg-primary', 'text-light'];
    $('#chat-receiver').on('click', '.destinator', function () {
        $(this).siblings().removeClass(clickedFormat);
        $(this).addClass(clickedFormat);
        let id = $(this).attr('data-id');
        startChat(id);
    });
}

function startChat(id){
    window.destination_id = id;
    disableChatController();
    removeChatMessages();
    loadOldMessages(id);
}

function loadOldMessages(id){
    $.ajax({
        type: "get",
        url: "/chat/message/",
        data: {
            role: window.role,
            id: id,
        },
        dataType: "json",
        success: function (response) {
            response.forEach(element => {
                let role = element.role;
                if (role == window.role){
                    sendMessage(element.message, element.image);
                } else {
                    recvMessage(element.message, element.image);
                }
            });
            createChatSocket(id);
        }
    });
}

function removeChatMessages(){
    $('.messages').empty();
}

function disableChatController(){
    $('#send-button').prop('disabled', true);
    $('#chat-input').prop('disabled', true);
    $('#emoji-btn').prop('disabled', true);
    $('#image-btn').prop('disabled', true);
}

function enableChatController(){
    $('#send-button').prop('disabled', false);
    $('#chat-input').prop('disabled', false);
    $('#emoji-btn').prop('disabled', false);
    $('#image-btn').prop('disabled', false);
}

function recvMessage(message, image){
    let content = message;
    let is_image = content == '';
    let obj;
    if (is_image){
        obj = $(`
            <div class="row my-1 justify-content-start">
                <div class="col-md-6 row justify-content-start">
                    <div class="col-auto p-2 px-3">
                        <span><img src="${image}" alt="image" width="100vw" class="p-2 msg" role="button"></span>
                    </div>
                </div>
            </div>`);
    } else {
    obj = $(`
        <div class="row my-1 justify-content-start">
            <div class="col-md-6 row justify-content-start">
                <div class="col-auto border rounded-pill bg-light text-dark p-2 px-3">
                    <span>${content}</span>
                </div>
            </div>
        </div>`);
    }
    $('.messages').append(obj).scrollTop(function(){
        return this.scrollHeight;
    });
}

function sendMessage(message, image){
    let content = message;
    let is_image = content == '';
    let obj;
    if (is_image){
        obj = $(`
        <div class="row my-1 justify-content-end">
            <div class="col-md-6 row justify-content-end">
                <div class="col-auto p-2 px-3">
                    <span><img src="${image}" alt="image" width="100vw" class="p-2 msg" role="button"></span>
                </div>
            </div>
        </div>
        `);
    } else {
    obj = $(`
        <div class="row my-1 justify-content-end">
            <div class="col-md-6 row justify-content-end">
                <div class="col-auto border rounded-pill bg-primary text-light p-2 px-3">
                    <span>${content}</span>
                </div>
            </div>
        </div>
        `);
    }
    $('.messages').append(obj).scrollTop($('.messages')[0].scrollHeight);
}

function createChatSocket(id){
    window.chatSocket.close();
    window.chatSocket = new WebSocket('wss://' + window.location.host + `/ws/chat/${window.role}/${id}/`);
    window.chatSocket.onmessage = function (e) {
        let obj = JSON.parse(e.data);
        let message = obj.message;
        if (message.type == 'chat_message'){
            let data = message.data;
            if (data.sender == window.role){
                sendMessage(data.message, data.image_url);
            } else {
                recvMessage(data.message, data.image_url);
            }
        }

        let receivers = $('#chat-receiver .destinator');
        for (let i = 0; i < receivers.length; i++){
            let receiverId = receivers.eq(i).attr('data-id');
            if (id == receiverId){
                if (i > 0){
                    receivers.eq(i).insertBefore(receivers.eq(0));
                }
                break;
            }
        }
    };

    let pingWS = () => {
        if (window.chatSocket.readyState == 0){
            setTimeout(pingWS, 100);
        } else {
            if (window.chatSocket.readyState == 1){
                enableChatController();
            }
        }
    }

    pingWS();
}

function reload(){
    let params = {
        role: window.role,
        search: window.searchedName,
    };

    window.location.href = `/chat/?${$.param(params)}`;
}

function handleSelectRole(){
    $('.select-role').click(function () { 
        window.role = $(this).attr('data-role');
        reload();
    });
}

function handleSearch(){
    $('#name-search-btn').click(function (){
        window.searchedName = $('#name-search-input').val();
        reload();
    });

    $('#name-search-input').keyup(function (e) {
        if (e.keyCode == 13){
            window.searchedName = $('#name-search-input').val();
            reload();
        }
    });
}