const url = new URL(window.location.href);
const id = new URLSearchParams(url.search).get('id');

const $back_button = document.getElementById("back");
const $expand_hw_button = document.getElementById("expand-hw");
const $expand_sw_button = document.getElementById("expand-sw");
const $expand_pr_button = document.getElementById("expand-pr");

$back_button.addEventListener("click", ()=>{
    location.href = "/employee-evaluation"
});

/**
 * Переход к конкретному блоку дисциплин
 */
$expand_hw_button.addEventListener("click", ()=>{
    fetch_block("hw");
});
$expand_sw_button.addEventListener("click", ()=>{
    fetch_block("sw");
});
$expand_pr_button.addEventListener("click", ()=>{
    fetch_block("pr");
});

/**
 * Переход на страницу с информацией о конкретном блоке дисциплин сотрудника
 * @param block_name
 */
function fetch_block(block_name){
    sessionStorage.setItem("ee_block", block_name);
    location.href = window.urls.employee_evaluation_about_block + "?" + new URLSearchParams({'block': block_name, 'id': id});
}