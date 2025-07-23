document.addEventListener('DOMContentLoaded', function() {
    const productSelect = document.getElementById('product-select');
    const disciplineSelect = document.getElementById('discipline-select');
    const levelSelect = document.getElementById('level-select');
    const resultsTable = document.getElementById('results-table');

    productSelect.addEventListener('change', function() {
        const product = this.value;
        if (product) {
            fetchDisciplines(product);
            disciplineSelect.disabled = false;
        } else {
            disciplineSelect.disabled = true;
            levelSelect.disabled = true;
            clearResults();
        }
    });

    disciplineSelect.addEventListener('change', function() {
        if (this.value) {
            levelSelect.disabled = false;
        } else {
            levelSelect.disabled = true;
            clearResults();
        }
    });

    levelSelect.addEventListener('change', function() {
        if (this.value) {
            fetchEmployees();
        } else {
            clearResults();
        }
    });

    function fetchDisciplines(product) {
        fetch(`${window.urls.selection_disciplines}${product}`)
            .then(response => response.json())
            .then(data => {
                disciplineSelect.innerHTML = '<option value="">Выберите дисциплину</option>';
                data.forEach(discipline => {
                    const option = document.createElement('option');
                    option.value = discipline;
                    option.textContent = discipline;
                    disciplineSelect.appendChild(option);
                });
            })
            .catch(error => {
                showSnackbar('Ошибка при загрузке дисциплин', 'error');
            });
    }

    function fetchEmployees() {
        const params = {
            product: productSelect.value,
            discipline: disciplineSelect.value,
            level: levelSelect.value
        };

        fetch(window.urls.selection_employees + '?' + new URLSearchParams(params))
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                showSnackbar('Ошибка при загрузке сотрудников', 'error');
            });
    }

    function displayResults(employees) {
        resultsTable.innerHTML = '';

        if (employees.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="3" class="text-center">Сотрудники не найдены</td>
            `;
            resultsTable.appendChild(row);
            return;
        }

        employees.forEach(employee => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${employee.name}</td>
                <td>${employee.level}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="showEmployeeDetails('${employee.id}')">
                        <i class="bi bi-info-circle"></i>
                    </button>
                </td>
            `;
            resultsTable.appendChild(row);
        });
    }

    function clearResults() {
        resultsTable.innerHTML = '';
    }
});

function showEmployeeDetails(employeeId) {
    // Реализация показа деталей сотрудника
    // Можно добавить модальное окно с подробной информацией
}