function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function showImageViewer(url){
    $('#show-img').attr('src', url);
    $('#image-viewer').modal('show');
}

export function csrftoken(){
    return getCookie('csrftoken');
}

export function csrfHeader(){
    return {
        'X-CSRFToken': csrftoken(),
    }
}

function getCartNumber(){
    return $('#cart-size').text();
}

export function increaseCartNumber(){
    $('#cart-size').text(parseInt(getCartNumber()) + 1);
}

export function decreaseCartNumber(){
    $('#cart-size').text(parseInt(getCartNumber()) - 1);
}

export function createToast(message, bg){
    let toast = document.createElement('div');
    toast.classList.add('toast');
    toast.classList.add('bg-' + bg);
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    let title = gettext('Notification'),
        time = gettext('just now');
    toast.innerHTML = 
    `<div class="toast-header">
        <i class="fa-solid fa-circle-exclamation me-2"></i>
        <strong class="me-auto">${title}</strong>
        <small>${time}</small>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body text-light">
        ${message}
    </div>`;
    return toast;
}

export function showToast(message, bg='success'){
    let toast = createToast(message, bg);
    $('.toast-container').append(toast);
    let toastInstance = new bootstrap.Toast(toast);
    toastInstance.show();
}