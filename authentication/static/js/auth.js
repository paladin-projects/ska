import { initializePasswordValidation, initializePasswordToggles } from '/static/js/passwordValidation.js';

document.addEventListener('DOMContentLoaded', () => {

    // Инициализация переключателей видимости пароля
    initializePasswordToggles();

    const forms = {
        login: document.getElementById("login-form"),
        registration: document.getElementById("reg")
    };

    if (forms.login) {
        forms.login.addEventListener("submit", async (evt) => {
            evt.preventDefault();

            try {
                const response = await fetch(window.urls.auth_login, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: new FormData(forms.login)
                });

                if (response.ok) {
                    const urlParams = new URLSearchParams(window.location.search);
                    window.location.href = urlParams.get('next') || '/';
                }

                else {
                    const text = await response.text();
                    showSnackbar(text || "Ошибка при входе");
                }
            }

            catch (error) {
                showSnackbar("Произошла ошибка при попытке входа");
            }
        });
    }
});

if (forms.registration) {
    const $password = document.getElementById("password");
    const $rePassword = document.getElementById("re-password");
    const $username = document.getElementById("username");
    const $email = document.getElementById("email");
    const form = document.getElementById("reg");

    // Инициализация валидации паролей
    const validatePasswords = initializePasswordValidation({
        passwordInput: $password,
        confirmPasswordInput: $rePassword,
        minLength: 8,
        onValidationError: (message) => showSnackbar(message, 'error')
    });

    form.addEventListener("submit", async (evt) => {
        evt.preventDefault();

        // Валидация паролей
        if (!validatePasswords()) return;

        // Валидация email
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test($email.value)) {
            showSnackbar("Введите корректный email адрес", 'error');
            return;
        }

        // Валидация имени пользователя
        if ($username.value.length < 3) {
            showSnackbar("Имя пользователя должно содержать минимум 3 символа", 'error');
            return;
        }

        const formData = new FormData(form);

        try {
            const response = await fetch(window.urls.auth_registration, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new FormData(form)
            });

            if (response.redirected) {
                window.location.href = response.url;
            }

            else if (response.ok) {
                const urlParams = new URLSearchParams(window.location.search);
                window.location.href = urlParams.get('next') || '/';
            }

            else {
                const text = await response.text();
                showSnackbar(text || "Ошибка при регистрации", 'error');
            }
        }

        catch (error) {
            console.error('Ошибка:', error);
            showSnackbar("Произошла ошибка при отправке данных", 'error');
        }
    });

    // Сброс стиля границы при вводе
    $username.addEventListener("input", () => {
        $username.style.borderColor = "";
    });
}