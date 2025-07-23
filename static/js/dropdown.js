// Инициализация обработчиков для выпадающего списка
function initDropdown(containerSelector = '.dropdown') {
    document.querySelectorAll(containerSelector).forEach(dropdown => {
        const input = dropdown.querySelector('input[type="hidden"]');
        const selectedText = dropdown.querySelector('.selected-department');
        const dropdownItems = dropdown.querySelectorAll('.dropdown-item');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        const dropdownToggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');

        // Функция для расчета позиции меню
        function calculateMenuPosition() {
            const toggleRect = dropdownToggle.getBoundingClientRect();
            const menuRect = dropdownMenu.getBoundingClientRect();
            const windowHeight = window.innerHeight;

            // Поиск ближайшего родительского контейнера с overflow
            let parent = dropdown.parentElement;
            let containerRect = null;

            while (parent && !containerRect) {
                const overflow = window.getComputedStyle(parent).overflow;

                if (overflow === 'auto' || overflow === 'scroll' || parent.classList.contains('card-body')) {
                    containerRect = parent.getBoundingClientRect();
                    break;
                }

                parent = parent.parentElement;
            }

            containerRect = containerRect || {
                top: 0,
                bottom: windowHeight,
                height: windowHeight
            };

            // Проверки позиционирования
            const spaceBelow = containerRect.bottom - toggleRect.bottom;
            const spaceAbove = toggleRect.top - containerRect.top;
            const needsUpward = spaceBelow < menuRect.height && spaceAbove > menuRect.height;

            if (needsUpward) {
                dropdownMenu.style.bottom = '100%';
                dropdownMenu.style.top = 'auto';
                dropdownMenu.style.maxHeight = `${Math.floor(spaceAbove)}px`;
                dropdownMenu.style.transform = 'translateY(-0.25rem)';
            }

            else {
                dropdownMenu.style.top = '100%';
                dropdownMenu.style.bottom = 'auto';
                dropdownMenu.style.maxHeight = `${Math.floor(spaceBelow)}px`;
                dropdownMenu.style.transform = 'translateY(0.25rem)';
            }

            dropdownMenu.style.overflowY = 'auto';
        }

        // Обработчик клика по кнопке
        dropdownToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const isVisible = dropdownMenu.classList.contains('show');

            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
                menu.parentElement.querySelector('[data-bs-toggle="dropdown"]').setAttribute('aria-expanded', 'false');
            });

            if (!isVisible) {
                dropdownMenu.classList.add('show');
                dropdownToggle.setAttribute('aria-expanded', 'true');
                calculateMenuPosition();
            }
        });

        // Обработчик выбора элемента
        dropdownItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                const value = item.dataset.value;
                const text = item.textContent.trim();

                // Обновление значения скрытого input и текста кнопки
                if (input) input.value = value;
                if (selectedText) selectedText.textContent = text;

                // Обновление активного элемента
                dropdownItems.forEach(di => di.classList.remove('active'));
                item.classList.add('active');

                // Пересчет позиции после обновления активного элемента
                calculateMenuPosition();
            });
        });

        // Закрытие при клике вне dropdown
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdownMenu.classList.remove('show');
                dropdownToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Обновление позиции при прокрутке и изменении размера окна
        const updatePosition = () => {
            if (dropdownMenu.classList.contains('show')) {
                calculateMenuPosition();
            }
        };

        // Использование throttle для оптимизации
        let ticking = false;
        const throttledUpdate = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    updatePosition();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', throttledUpdate, { passive: true });
        window.addEventListener('resize', throttledUpdate, { passive: true });
    });
}

export { initDropdown };