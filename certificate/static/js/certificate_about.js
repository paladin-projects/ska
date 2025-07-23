const $delete_confirmation_modal = document.getElementById("delete-confirmation-modal");

const $delete_button = document.getElementById("delete");
const $confirm_delete_button = document.getElementById("confirm-delete");
const $cancel_delete_button = document.getElementById("cancel-delete");

/**
 * Функция для удаления сертификата
 */
$delete_button.addEventListener("click", ()=>{
//    console.log("clicked");
    $delete_confirmation_modal.showModal();
});

/**
 * Функция для отправки запроса на удаление после подтверждения удаления в модальном окне
 */
$confirm_delete_button.addEventListener("click", ()=>{
    $delete_confirmation_modal.close();
    fetch(window.urls.certificate_delete, {
        method: "POST",
        headers:{"X-CSRFToken": document.querySelector('input[name="csrfmiddlewaretoken"]').value},
        body: new URLSearchParams({"id": document.getElementById("id").textContent})
    }).then(resp => {
        if (resp.ok){
            showSnackbar("Сертификат удален!");
        }
    });
});

/**
 * Закрытие модального окна в случае отмены удаления сертификата
 */
$cancel_delete_button.addEventListener("click", ()=>{
    $delete_confirmation_modal.close();
})