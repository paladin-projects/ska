const searchField = document.getElementById('search-field');
const employeeCards = document.querySelectorAll('.employee-card');

searchField.addEventListener('input', (e) => {
    const searchValue = e.target.value.toLowerCase();

    employeeCards.forEach(card => {
        const employeeName = card.querySelector('.employee-info h3').textContent.toLowerCase();
        const department = card.querySelector('.employee-info p').textContent.toLowerCase();

        if (employeeName.includes(searchValue) || department.includes(searchValue)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});

employeeCards.forEach(card => {
    card.addEventListener('click', () => {
        const employeeId = card.dataset.id;
        location.href = `${window.urls.employee_evaluation_about}?id=${employeeId}`;
    });
});