document.addEventListener('DOMContentLoaded', function() {
    const uploadButton = document.getElementById('upload-certificate');
    const certificateModal = new bootstrap.Modal(document.getElementById('certificateModal'));
    const certificateForm = document.getElementById('certificate-form');

    uploadButton.addEventListener('click', () => {
        certificateModal.show();
    });

    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const selectedCategory = this.value;

            document.querySelectorAll('.subcategory-chip').forEach(chip => {
                chip.classList.remove('visible');
                setTimeout(() => {
                    chip.style.display = 'none';
                    const radio = chip.querySelector('input[type="radio"]');
                    if (radio.checked) {
                        radio.checked = false;
                    }
                }, 300);
            });

            document.querySelectorAll(`.subcategory-chip[data-category="${selectedCategory}"]`)
                .forEach((chip, index) => {
                    setTimeout(() => {
                        chip.style.display = 'inline-block';
                        setTimeout(() => {
                            chip.classList.add('visible');
                        }, index * 50);
                    }, 300);
                });
        });
    });

    certificateForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const requiredFields = this.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value) {
                isValid = false;
                if (field.type === 'radio') {
                    const radioGroup = field.closest('.radio-cards, .chips-container');
                    if (radioGroup) {
                        radioGroup.classList.add('is-invalid');
                    }
                } else {
                    field.classList.add('is-invalid');
                }
            } else {
                if (field.type === 'radio') {
                    const radioGroup = field.closest('.radio-cards, .chips-container');
                    if (radioGroup) {
                        radioGroup.classList.remove('is-invalid');
                    }
                } else {
                    field.classList.remove('is-invalid');
                }
            }
        });

        if (!isValid) {
            showSnackbar('Пожалуйста, заполните все обязательные поля', 'error');
            return;
        }

        fetch(window.urls.certificate_main, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new FormData(this)
        })
        .then(response => {
            if (response.ok) {
                showSnackbar('Сертификат успешно загружен', 'success');
                certificateModal.hide();
                location.reload();
            } else {
                return response.text().then(text => {
                    showSnackbar(text || 'Ошибка при загрузке сертификата', 'error');
                });
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showSnackbar('Произошла ошибка при отправке данных', 'error');
        });
    });

    document.getElementById('certificateModal').addEventListener('hidden.bs.modal', function () {
        certificateForm.reset();

        document.querySelectorAll('.subcategory-chip').forEach(chip => {
            chip.style.display = 'none';
        });

        document.querySelectorAll('.is-invalid').forEach(element => {
            element.classList.remove('is-invalid');
        });

        document.querySelectorAll('.radio-card-content, .chip-content').forEach(element => {
            element.classList.remove('selected');
        });
    });

    document.querySelectorAll('.radio-card, .chip').forEach(element => {
        element.addEventListener('mouseover', function() {
            this.querySelector('.radio-card-content, .chip-content')
                ?.classList.add('hover');
        });

        element.addEventListener('mouseout', function() {
            this.querySelector('.radio-card-content, .chip-content')
                ?.classList.remove('hover');
        });
    });

    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const container = this.closest('.radio-cards, .chips-container');
            if (container) {
                container.querySelectorAll('.radio-card-content, .chip-content')
                    .forEach(el => el.classList.remove('selected'));
                container.classList.remove('is-invalid');
            }

            const content = this.nextElementSibling;
            if (content) {
                content.classList.add('selected');
            }
        });
    });
});