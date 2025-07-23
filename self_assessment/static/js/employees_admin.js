document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('id_role');
    const departmentField = document.getElementById('id_department');
    const subordinateField = document.getElementById('id_subordinate_of');

    function updateFields() {
        const selectedRole = roleSelect.value;
        const departmentRow = departmentField?.closest('.form-row');
        const subordinateRow = subordinateField?.closest('.form-row');

        if (departmentRow && departmentField) {
            departmentRow.style.display = '';

            if (selectedRole === 'admin') {
                departmentField.disabled = true;
                departmentField.value = '';
                departmentField.required = false;
            }

            else {
                departmentField.disabled = false;
                departmentField.required = true;
            }
        }

        if (subordinateRow && subordinateField) {
            subordinateRow.style.display = '';

            if (selectedRole === 'employee') {
                subordinateField.disabled = false;
                subordinateField.required = true;
            }

            else {
                subordinateField.disabled = true;
                subordinateField.value = '';
                subordinateField.required = false;
            }
        }
    }

    if (roleSelect) {
        roleSelect.addEventListener('change', updateFields);

        // Вызываем функцию при загрузке страницы
        updateFields();
    }
});