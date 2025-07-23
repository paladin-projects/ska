import { initializePasswordValidation, initializePasswordToggles } from '/static/js/passwordValidation.js';

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация компонентов
    const sections = document.querySelectorAll('.profile-section');

    /**
     * Показывает выбранную секцию
     * @param {string} sectionId - идентификатор секции
     */
    function showSection(sectionId) {
        sections.forEach(section => {
            section.style.display = 'none';
            section.classList.remove('active');
        });

        const selectedSection = document.getElementById(`${sectionId}-section`);
        if (selectedSection) {
            selectedSection.style.display = 'block';
            setTimeout(() => {
                selectedSection.classList.add('active');
            }, 50);
        }
    }

    // Обработчики событий для навигации
    document.querySelectorAll('input[name="profile-section"]').forEach(input => {
        input.addEventListener('change', function() {
            showSection(this.value);
        });

        // Инициализация начального состояния
        if (input.checked) {
            showSection(input.value);
        }
    });

    initializePasswordToggles();

    /**
     * Обработка формы личной информации
     */
    const personalForm = document.getElementById('personal-form');
    if (personalForm) {
        personalForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            try {
                const response = await fetch('/profile/update/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: new FormData(this),
                });

                if (response.ok) {
                    showSnackbar('Профиль успешно обновлен');
                    setTimeout(() => location.reload(), 1500);
                }

                else {
                    const error = await response.text();
                    showSnackbar(error || 'Произошла ошибка при обновлении профиля', 'error');
                }
            }

            catch (error) {
                showSnackbar('Произошла ошибка при обновлении профиля', 'error');
            }
        });
    }

    /**
     * Обработка формы безопасности
     */
    const securityForm = document.getElementById('security-form');
    if (securityForm) {

        // Инициализация валидации паролей
        const newPassword = securityForm.querySelector('[name="new_password"]');
        const confirmPassword = securityForm.querySelector('[name="confirm_password"]');

        const validatePasswords = initializePasswordValidation({
            passwordInput: newPassword,
            confirmPasswordInput: confirmPassword,
            minLength: 8,
            onValidationError: (message) => showSnackbar(message, 'error')
        });

        securityForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Проверка валидности паролей перед отправкой
            if (!validatePasswords()) {
                return;
            }

            try {
                const response = await fetch(window.urls.profile_update, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: new FormData(this),
                });

                if (response.ok) {
                    showSnackbar('Пароль успешно изменен');
                    this.reset();

                    // Сброс стилей полей после успешного обновления
                    newPassword.style.borderColor = "";
                    confirmPassword.style.borderColor = "";
                }

                else {
                    const error = await response.text();
                    showSnackbar(error || 'Произошла ошибка при изменении пароля', 'error');
                }
            }

            catch (error) {
                showSnackbar('Произошла ошибка при изменении пароля', 'error');
            }
        });
    }
});