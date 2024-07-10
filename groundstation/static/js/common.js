$.ajaxSetup({
    crossDomain: false,
    beforeSend: function(xhr) {
        xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
    }
});

function dialog(header, message, confirm_cb, cancel_cb=() => {}) {
    $("#dialog-header h3").text(header);
    $("#dialog-body span").text(message);

    const $confirm_btn = $("#dialog-btn-yes");
    const $cancel_btn = $("#dialog-btn-no");
    const dialog_box = document.getElementById("dialog-box");

    const clean_up = function() {
        $confirm_btn.off();
        $cancel_btn.off();
        dialog_box.close();
    }

    $confirm_btn.on("click", function() {
        confirm_cb();
        clean_up();
    })

    $cancel_btn.on("click", function() {
        cancel_cb();
        clean_up();
    })

    dialog_box.showModal();
}
