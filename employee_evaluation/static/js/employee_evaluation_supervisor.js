// TODO добавить возможность скачивать сертификаты
const $filters = document.getElementById("filters");
const $supervisor_switch = document.getElementById("supervisor-switch");
const $cert__class = document.getElementById("class");
const $cert__subclass = document.getElementById("sub-class");

const $task_select = document.querySelectorAll(".task")
const $add_filter_button = document.querySelectorAll(".add-filter")
const $employees = document.querySelectorAll(".employee");

const $table = document.getElementById("employees-table")

let subordinates = [];
let filters = {};
let filterIDCounter = -1;

/**
 * Превентивный запрос списка подчиненных
 */
document.addEventListener("DOMContentLoaded", ()=>{
    fetch(window.urls.employee_evaluation_subordinates, {method: "GET"}).then(resp =>{
        if (resp.ok){
            resp.text().then(data=>{
                subordinates = JSON.parse(data).data
                $employees.forEach(function (el) {

                    // Проверяем роль сотрудника
                    const role = el.dataset.role;

                    if (role === 'employee' && subordinates.indexOf(Number(el.querySelector("td").textContent)) !== -1){
                        el.classList.toggle("subordinate");
                    }
                });
            });
        }
    });
});
/**
 * Раскрытие/закрытие блока с фильтрами
 * В этом режиме в списке сотрудников остаются только прямые подчиненные
 */
$supervisor_switch.addEventListener("click", (ev)=>{
    if (ev.target.checked) {
        $filters.classList.toggle("expanded");
        $employees.forEach(function (el) {
            if (!el.classList.contains("subordinate")) {
                el.style.display = "none"
            }
        });
    } else {
        $filters.classList.toggle("expanded");
        clearFiltersFromTable();
        disableSupervisor();
    }
});

/**
 * Метод, меня��щий поля фильтра в зависимости от того, по какому значению ставится фильтр:
 * Total - суммарный счет по дисциплине - числовой
 * Дисциплина - уровень - выбор уровня
 */
$task_select.forEach(function (el) {
    el.addEventListener("click", function (evt){
        let node = evt.target;
        if (node.value !== "Total"){
            node.parentNode.querySelector(".filter_value").style.display = 'none';
            node.parentNode.querySelector(".level").style.display = 'inline-block';
        }
        else {
            node.parentNode.querySelector(".filter_value").style.display = 'inline-block';
            node.parentNode.querySelector(".level").style.display = 'none';
        }
    });
});
/**
 * Добавление фильтра, в зависимости от блока, к которому он добавляется, зависит его формат
 */
$add_filter_button.forEach(el => {
    el.addEventListener("click", ()=> {
        let node = el.parentNode;
        let filter = {};

        const getValue = (selector) => node.querySelector(selector).value;

        switch (node.id) {
            case "hw":
            case "sw":
                filter = {
                    "id":getID(),
                    "block": node.id,
                    "product": getValue(".product"),
                    "task": getValue(".task"),
                    "sign": getValue(".sign")
                };

                if (filter["task"] === "Total") {
                    filter["value"] = getValue(".filter_value");
                    if (filter["value"] === ""){
                        showSnackbar("Введите значение для фильтра!");
                        return;
                    }
                } else {
                    filter["value"] = getValue(".level");
                }
                break;
            case "pr":
                filter = {
                    "id":getID(),
                    "block": "pr",
                    "process": getValue(".process"),
                    "sign": getValue(".sign"),
                    "value": getValue(".level"),
                    };
                break;
            case "cr":
                if (getValue("#class") === "any"){
                    showSnackbar("Укажите класс сертификата!")
                    return;
                }
                filter = {
                    "id":getID(),
                    "block": "cr",
                    "category": $cert__class.value,
                    "subcategory": $cert__subclass.value
                };
                break;
            default:
                showSnackbar(`Не понятно, из какого блока фильтр ${node.id}!`);
                return;
        }
        filters[filter.id] = filter;
        node.querySelector(".filters").innerHTML +=
            `<span class="filter" data-id="${filter["id"]}">` +
                `<span class="filter--data">${filterToString(filter)}</span>` +
                `<button class="delete-filter" onclick="` +
                    `delete filters[this.parentNode.dataset.id];`+
                    `this.parentNode.remove();` +
                `">x</button>` +
            `</span>`;
    });
});

/**
 * Изменение отображаемых подклассов сертификатов, в зависимости от класса
 */
$cert__class.addEventListener("change", ()=>{
    $cert__subclass.querySelectorAll("option").forEach(function (el){
        if (!el.classList.contains($cert__class.value)){
            el.style.display = 'none';
        } else {
            el.style.display = 'block';
        }
    });
    $cert__subclass.querySelector("option.DF").selected = true;
});

/**
 * Строков��е представление фильтра для его отображения в добавленные
 * @param filter объект фильтра
 * @return {string} строковое представление фильтра
 */
function filterToString(filter){
    switch (filter["block"]) {
        case "hw":
        case "sw":
            return `${filter["product"]}: ${filter["task"]} ${filter["sign"]} ${filter["value"]}`;
        case "pr":
            return `${filter["process"]} ${filter["sign"]} ${filter["value"]}`;
        case "cr":
            return `${filter["category"]}: ${filter["subcategory"]}`;
        default:
            return "unknown filter";
    }
}

/**
 * Простенький генератор для создания id фильтров, чтобы их было проще удалять
 * @return {number}
 */
function getID() {
    filterIDCounter++
    return filterIDCounter;
}
/**
 * Очищает массив фильтров, удаляет сами фильтры, возвращает видимость всех сотрудников при выходе из "режима начальника",
 */
function disableSupervisor(){
    document.querySelectorAll(".filters").forEach((el)=>{
        el.innerHTML = "";
    });
    filters = [];
    $employees.forEach(function (el) {
        el.style.display = "table-row";
    });
}
/**
 * Отправляет список фильтров и id сотрудников для фильтрации на сервер
 */
function sendFilters() {
    if (Object.keys(filters).length === 0) {
        showSnackbar("Сначала добавьте фильтры!")
        return
    }

    fetch(window.urls.employee_evaluation_subordinates_filter, {
        method: "POST",
        headers:{"X-CSRFToken": document.querySelector('input[name="csrfmiddlewaretoken"]').value},
        body: new URLSearchParams({"data": JSON.stringify({subordinates: subordinates, filters: filters})}),
    }).then(resp => {
       if (resp.ok) {
           resp.text().then(msg => {

               clearFiltersFromTable();

               /**
                * @type {{employees_id: Array, data_for_table: Array}}
                */
               let d = JSON.parse(msg);
               let matches = d.employees_id;
               let data_for_table = d.data_for_table;


               document.querySelectorAll(".subordinate").forEach(el =>{
                   if (matches.indexOf(Number(el.querySelector("td").textContent)) === -1) {
                       el.style.display = 'none';
                   } else {
                       el.style.display = 'table-row';
                   }

               });

               appendHeadersToTable($table.querySelector("thead > tr"));
               appendRowsToTable(data_for_table, $table.querySelectorAll(".subordinate"))
           });
       } else if (resp.status === 404) {
           resp.text().then(e =>{
               showSnackbar("После отмеченного фильтра осталось 0 сущнос��ей для фильтрации!");
               document.querySelector(`.filter[data-id="${e}"]`).classList.add("failing-filter");
           });
       }
    });
}
/**
 * Расширяет таблицу, создавая заголовки для колонок, отражающих фильтруемые значения
 * @param headerSelector
 */
function appendHeadersToTable(headerSelector) {
    let buff;
    for (const i in filters) {
        let th = document.createElement("th");
        th.classList.add("tmp-table");
        buff = filters[i];
        switch (buff["block"]) {
            case "hw":
            case "sw":
                th.textContent = `${buff["product"]}:${buff["task"]}`;
                break;
            case "pr":
                th.textContent = buff["process"];
                break;
            case "cr":
                th.textContent = buff["category"];
                break;
        }
        headerSelector.append(th);
    }
}

/**
 * Дополняет строки-записи о сотрудниках, прошедших фильтры, дописывая значения, по которым их фильтровали
 * @param data {Array}
 * @param rowsSelector {NodeListOf<HTMLTableRowElement>}
 */
function appendRowsToTable(data, rowsSelector) {
    // const start= new Date().getTime();
    // let tds = ""
    // for (let i = 0; i < rowsSelector.length; i++) {
    //     let id = rowsSelector[i].querySelector("td").textContent
    //     for (let d in data[id]) {
    //         tds += `<td class="tmp-table">${data[id][d]}</td>`
    //     }
    //     rowsSelector[i].innerHTML += tds
    //     tds = ""
    // }

    for (let i = 0; i < rowsSelector.length; i++) {
        let id = rowsSelector[i].querySelector("td").textContent
        for (let d in data[id]) {
            let td = document.createElement("td")
            td.classList.add("tmp-table");
            td.textContent = data[id][d];
            rowsSelector[i].append(td)
        }
    }

    // const end = new Date().getTime();
    // console.log(`SecondWay: ${end - start}ms`);
    // console.log(`start: ${start}, end: ${end}`);

}
/**
 * Метод для удаления из таблицы временных строк\колонок, которые были созданы для отображения результатов фильтрации
 */
function clearFiltersFromTable() {
    document.querySelectorAll(".tmp-table").forEach(el => {
        el.remove()
    })
}

/**
 * Позволяет сохранить таблицу с отобранными сотрудник��ми в csv формате
 */
function saveCSV() {
    let csv_data = [];

    $table.querySelectorAll("tr").forEach(el => {
        let cols = el.querySelectorAll('tr.subordinate td,th');

        if (cols.length !== 0) {
            let row = [];
            for (let j = 0; j < cols.length; j++) {
                row.push(cols[j].textContent);
            }
            csv_data.push(row.join(","));
        }

    });
    csv_data = csv_data.join('\n');

    let CSVFile = new Blob([csv_data], { type: "text/csv" });

    let temp_link = document.createElement('a');

    temp_link.download = "filtered_employees.csv";
    temp_link.href = window.URL.createObjectURL(CSVFile);

    temp_link.style.display = "none";
    document.body.appendChild(temp_link);

    temp_link.click();
    document.body.removeChild(temp_link);
}