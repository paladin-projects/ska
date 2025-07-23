const assessmentData = {
    hw: { count: 0, total: 0, selections: {} },
    sw: { count: 0, total: 0, selections: {} },
    pr: { count: 0, total: 0, selections: {} }
};

const modal = new bootstrap.Modal(document.getElementById('restoreModal'));

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация блоков и подсчет вопросов
    Object.keys(assessmentData).forEach(blockId => {
        const block = document.getElementById(`products_${blockId}`);

        if (block) {
            const inputs = block.querySelectorAll('input[type="radio"][required]');
            const uniqueNames = new Set(Array.from(inputs).map(input => input.name));
            assessmentData[blockId].total = uniqueNames.size;
        }

        else {
            console.error(`Block with id products_${blockId} not found`);
        }
    });

    // Обработка выбора направления
    document.querySelectorAll('.direction-card').forEach(card => {
        card.addEventListener('click', () => {
            const direction = card.dataset.direction;
            document.querySelector('.direction-selection').style.display = 'none';
            const mainContent = document.querySelector('.main-content');
            mainContent.style.display = 'block';

            // Обновление заголовка
            const directionTitle = mainContent.querySelector('.direction-title');
            directionTitle.textContent = card.querySelector('.direction-name').textContent;

            // Инициализация блока продуктов для выбранного направления
            document.querySelectorAll('.products-block').forEach(block => {
                block.style.display = 'none';
            });
            document.getElementById(`products_${direction}`).style.display = 'grid';

            // Заполнение списка задач
            const tasksList = mainContent.querySelector('.tasks-list');
            const tasks = new Set();
            document.querySelectorAll(`#products_${direction} .product-card`).forEach(card => {
                const cardTasks = card.dataset.tasks.split(',');
                cardTasks.forEach(task => tasks.add(task));
            });

            tasksList.innerHTML = `
                <div class="filter-chips">
                    ${Array.from(tasks).map(task => `
                        <label class="chip">
                            <input type="checkbox" name="task_filter" value="${task}">
                            <span>${task}</span>
                        </label>
                    `).join('')}
                </div>
            `;

            document.getElementById('finish-button').style.display = 'block';
        });
    });

    // Обработка кнопки "Назад"
    document.querySelector('.back-button').addEventListener('click', () => {
        document.querySelector('.direction-selection').style.display = 'grid';
        document.querySelector('.main-content').style.display = 'none';
    });

    // Обработка поиска и фильтрации
    const searchInput = document.querySelector('.search-input');
    searchInput.addEventListener('input', (e) => {
        const searchText = e.target.value.toLowerCase();
        document.querySelectorAll('.chip').forEach(chip => {
            const taskName = chip.querySelector('span').textContent.toLowerCase();
            chip.style.display = taskName.includes(searchText) ? 'inline-block' : 'none';
        });
    });

    // Обработка фильтрации по задачам
    document.querySelector('.tasks-list').addEventListener('change', (e) => {

        if (e.target.type === 'checkbox') {
            const selectedTasks = Array.from(document.querySelectorAll('input[name="task_filter"]:checked'))
                .map(input => input.value);

            document.querySelectorAll('.product-card').forEach(card => {
                const cardTasks = card.dataset.tasks.split(',');

                if (selectedTasks.length === 0 || cardTasks.some(task => selectedTasks.includes(task))) {
                    card.style.display = 'block';
                }

                else {
                    card.style.display = 'none';
                }
            });
        }
    });

    // Обработка клика по продукту
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', () => {
            const details = card.querySelector('.product-details');

            if (details.style.display === 'none') {
                document.querySelectorAll('.product-details').forEach(d => {
                    d.style.display = 'none';
                });
                details.style.display = 'block';
            }

            else {
                details.style.display = 'none';
            }
        });
    });

    // Обработка выбора ответов
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            e.stopPropagation();

            const blockId = e.target.closest('.products-block').id.replace('products_', '');
            const inputName = e.target.name;
            const inputValue = e.target.value;

            if (!assessmentData[blockId].selections[inputName]) {
                assessmentData[blockId].count++;
            }
            assessmentData[blockId].selections[inputName] = inputValue;

            saveFormData();
        });
    });

    // Обработка кнопки завершения
    const finishButton = document.getElementById('finish-button');
    if (finishButton) {
        finishButton.addEventListener('click', () => {

            if (isFormComplete()) {
                const formData = collectFormData();
                submitForm(formData);
            }

            else {
                showSnackbar("Сначал выберите ответ во всех вопросах!", 'warning');
            }
        });
    }

    // Обработка модального окна
    document.getElementById('modal-accept')?.addEventListener('click', () => {
        restoreFormData();
        modal.hide();
    });

    document.getElementById('modal-decline')?.addEventListener('click', () => {
        localStorage.removeItem('SKA_DATA');
        modal.hide();
    });

    // Проверка сохраненных данных
    const savedData = localStorage.getItem('SKA_DATA');
    if (savedData) {
        modal.show();
    }

    // Инициализация обработчиков для иконок
    initializeIconAnimations();
});

function initializeIconAnimations() {
    const cards = document.querySelectorAll('.direction-card');

    cards.forEach(card => {
        const icon = card.querySelector('.direction-icon');
        const iconI = icon.querySelector('i');
        let pulseTimeout = null;
        let isReturning = false;

        // Обработка состояния покоя иконки
        icon.classList.add('at-rest');

        function resetIconState() {
            icon.style.animation = 'none';
            iconI.style.animation = 'none';
            icon.style.transform = '';
            iconI.style.transform = '';
            icon.offsetHeight;
            iconI.offsetHeight;
            icon.style.animation = '';
            iconI.style.animation = '';
            iconI.classList.remove('pulse-ready');
            clearTimeout(pulseTimeout);
            isReturning = false;
        }

        function startPulseAnimation() {

            if (card.matches(':hover') && !isReturning) {
                iconI.classList.add('pulse-ready');
            }
        }

        card.addEventListener('mouseenter', () => {

            if (isReturning) {
                icon.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                iconI.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

                requestAnimationFrame(() => {
                    resetIconState();
                    icon.classList.remove('at-rest');
                    pulseTimeout = setTimeout(startPulseAnimation, 600);
                });
            }

            else {
                resetIconState();
                requestAnimationFrame(() => {
                    icon.classList.remove('at-rest');
                    pulseTimeout = setTimeout(startPulseAnimation, 600);
                });
            }
        });

        card.addEventListener('mouseleave', () => {
            isReturning = true;
            resetIconState();

            icon.addEventListener('transitionend', () => {

                if (!card.matches(':hover')) {
                    requestAnimationFrame(() => {
                        icon.classList.add('at-rest');
                        isReturning = false;
                    });
                }
            }, { once: true });
        });

        card.addEventListener('mousedown', () => {
            resetIconState();
            clearTimeout(pulseTimeout);
        });

        card.addEventListener('mouseup', () => {

if (card.matches(':hover') && !isReturning) {
                pulseTimeout = setTimeout(startPulseAnimation, 300);
            }
        });
    });
}

// Вспомогательные функции
function isFormComplete() {
    return Object.values(assessmentData).every(block => block.count === block.total);
}

function collectFormData() {
    const data = {};
    Object.entries(assessmentData).forEach(([blockId, block]) => {
        data[blockId.toUpperCase()] = block.selections;
    });

    return data;
}

function submitForm(data) {
    const formData = new FormData();
    formData.append('data', JSON.stringify(data));

    fetch(window.urls.self_assessment_upload, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
    })
    .then(response => {

        if (response.ok) {
            showSnackbar("езультаты успешно сохранены!", 'success');
            const finishButton = document.getElementById('finish-button');

            if (finishButton) {
                finishButton.disabled = true;
            }
            localStorage.removeItem('SKA_DATA');
        }

        else {
            return response.text().then(text => {
                throw new Error(text || "Произошла ошибка при сохранении");
            });
        }
    })
    .catch(error => {
        showSnackbar(error.message, 'error');
    });
}

function saveFormData() {
    localStorage.setItem('SKA_DATA', JSON.stringify(collectFormData()));
}

function restoreFormData() {
    const savedData = JSON.parse(localStorage.getItem('SKA_DATA'));

    if (savedData) {
        Object.entries(savedData).forEach(([blockId, selections]) => {
            const localBlockId = blockId.toLowerCase();
            Object.entries(selections).forEach(([name, value]) => {
                const input = document.querySelector(`#products_${localBlockId} input[name="${name}"][value="${value}"]`);

                if (input) {
                    input.checked = true;
                    assessmentData[localBlockId].selections[name] = value;

                    if (!assessmentData[localBlockId].selections[name]) {
                        assessmentData[localBlockId].count++;
                    }
                }
            });
        });
    }
}