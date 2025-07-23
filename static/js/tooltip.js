class CustomTooltip {
    constructor() {
        this.tooltips = document.querySelectorAll('.custom-tooltip');
        this.tooltipContainer = this.createTooltipContainer();
        this.init();
    }

    createTooltipContainer() {
        const container = document.createElement('div');
        container.className = 'tooltip-container';
        document.body.appendChild(container);
        return container;
    }

    init() {
        this.moveTooltipsToContainer();
        this.initTooltipPositioning();
        this.initResizeHandler();
        this.initAccordionHandler();
    }

    moveTooltipsToContainer() {
        this.tooltips.forEach(tooltip => {
            const wrapper = tooltip.closest('.tooltip-wrapper');

            if (wrapper) {
                const tooltipId = `tooltip-${Math.random().toString(36).substr(2, 9)}`;
                wrapper.dataset.tooltipId = tooltipId;
                tooltip.dataset.for = tooltipId;
                this.tooltipContainer.appendChild(tooltip);
            }
        });
    }

    updateTooltipPosition(tooltip, wrapper) {
        const rect = wrapper.getBoundingClientRect();
        
        // Поиск ближайшего контейнера для определения границ
        const container = wrapper.closest('.accordion-body') || wrapper.closest('.card-body');
        const containerRect = container ? container.getBoundingClientRect() : { top: 0, bottom: window.innerHeight };
        
        // Поиск основной карточки
        const mainCard = wrapper.closest('.card-sidebar') || wrapper.closest('.card-main');
        const mainCardRect = mainCard ? mainCard.getBoundingClientRect() : { left: 0, right: window.innerWidth };

        // Сброс предыдущих классов позиционирования
        tooltip.classList.remove('tooltip-right', 'tooltip-left', 'tooltip-top', 'tooltip-bottom');

        // Инициализация tooltip для измерения
        tooltip.style.visibility = 'hidden';
        tooltip.style.opacity = '0';
        tooltip.style.display = 'block';
        const tooltipRect = tooltip.getBoundingClientRect();

        // Определение доступного пространства относительно окна браузера
        const spaceRight = Math.min(window.innerWidth - rect.right - 20, mainCardRect.right - rect.right - 20);
        const spaceLeft = Math.min(rect.left - 20, rect.left - mainCardRect.left - 20);
        const spaceTop = rect.top - (containerRect.top || 0) - 20;
        const spaceBottom = (containerRect.bottom || window.innerHeight) - rect.bottom - 20;

        // Выбор оптимального положения и установка позиции
        let position = '';
        let top = 0;
        let left = 0;

        if (spaceRight >= tooltipRect.width) {
            position = 'tooltip-right';
            top = rect.top + (rect.height / 2);
            left = rect.right + 10;
        }

        else if (spaceLeft >= tooltipRect.width) {
            position = 'tooltip-left';
            top = rect.top + (rect.height / 2);
            left = rect.left - tooltipRect.width - 10;
        }

        else if (spaceTop >= tooltipRect.height) {
            position = 'tooltip-top';
            top = rect.top - tooltipRect.height - 10;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        }

        else {
            position = 'tooltip-bottom';
            top = rect.bottom + 10;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        }

        // Применение позиции
        tooltip.style.position = 'fixed';
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
        tooltip.classList.add(position);

        // Возврат стилей отображения
        tooltip.style.display = '';
    }

    initTooltipPositioning() {
        document.querySelectorAll('.tooltip-wrapper').forEach(wrapper => {
            wrapper.addEventListener('mouseenter', () => {
                const tooltipId = wrapper.dataset.tooltipId;
                const tooltip = this.tooltipContainer.querySelector(`[data-for="${tooltipId}"]`);

                if (tooltip) {
                    this.updateTooltipPosition(tooltip, wrapper);
                    requestAnimationFrame(() => {
                        tooltip.style.visibility = 'visible';
                        tooltip.style.opacity = '1';
                    });
                }
            });

            wrapper.addEventListener('mouseleave', () => {
                const tooltipId = wrapper.dataset.tooltipId;
                const tooltip = this.tooltipContainer.querySelector(`[data-for="${tooltipId}"]`);

                if (tooltip) {
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.opacity = '0';
                }
            });
        });
    }

    initResizeHandler() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                document.querySelectorAll('.tooltip-wrapper').forEach(wrapper => {

                    if (wrapper.matches(':hover')) {
                        const tooltipId = wrapper.dataset.tooltipId;
                        const tooltip = this.tooltipContainer.querySelector(`[data-for="${tooltipId}"]`);

                        if (tooltip) {
                            this.updateTooltipPosition(tooltip, wrapper);
                        }
                    }
                });
            }, 100);
        });
    }

    initAccordionHandler() {
        document.querySelectorAll('.accordion-button').forEach(button => {
            button.addEventListener('click', () => {
                const collapse = document.querySelector(button.dataset.bsTarget);

                if (collapse) {
                    collapse.addEventListener('shown.bs.collapse', () => {
                        collapse.querySelectorAll('.tooltip-wrapper').forEach(wrapper => {

                            if (wrapper.matches(':hover')) {
                                const tooltipId = wrapper.dataset.tooltipId;
                                const tooltip = this.tooltipContainer.querySelector(`[data-for="${tooltipId}"]`);

                                if (tooltip) {
                                    this.updateTooltipPosition(tooltip, wrapper);
                                }
                            }
                        });
                    });
                }
            });
        });
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    new CustomTooltip();
});