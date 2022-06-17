import {showToast} from './utils.js';
$(function () {
    createWS();
});

function createWS(){
    window.chatSocket = new WebSocket('wss://' + window.location.host + `/ws/noti/`);
    window.chatSocket.onmessage = function (e) {
        let data = JSON.parse(e.data).data;
        if (data.type == 'notification'){
            let notiCount = parseInt($('#noti-size').text());
            $('#noti-size').text(notiCount + 1);
            showToast(gettext('You have new notification'));
        }

        if (data.type == 'chat'){
            showToast(gettext('You have new message'));
            if ((!window.role) || (data.role == window.role)) return;
            let message = data.message;
            for (let i = $('#chat-receiver .destinator').length - 1; i >= 0; i--) {
                if ($('#chat-receiver .destinator').eq(i).data('id') == message.from) {
                    if (i > 0){
                        $('#chat-receiver .destinator').eq(i).insertBefore($('#chat-receiver .destinator').eq(0));
                    }
                    return;
                }
            }
            let tel = gettext('Tel');
            $('#chat-receiver').prepend(`
                <div class="row border-bottom py-3 destinator" data-id="${message.from}" role="button">
                    <div class="col-sm-2">
                        <div class="position-relative">
                            <img src="${message.avatar}" class="img-fluid rounded" alt="">
                            <span class="position-absolute top-0 start-100 translate-middle p-2 text-success fw-bold">●</span>
                        </div>
                    </div>
                    <div class="col-sm-10">
                        <div class="row">
                            <span class="fw-bold">
                                ${message.name}
                            </span>
                        </div>
                        <div class="row">
                            <span> ${tel}:
                                ${message.tel}
                            </span>
                        </div>
                    </div>
                </div>
            `);
        }
    };

    let pingWS = () => {
        if (window.chatSocket.readyState == 0){
            setTimeout(pingWS, 100);
        } else {
            if (window.chatSocket.readyState == 1){
                console.log('ping');
            }
        }
    }

    pingWS();
}