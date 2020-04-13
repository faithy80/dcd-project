$(document).ready(function () {
    // initialization
    const max_ingredients = 500,
        max_method = 1500,
        ingredients = document.getElementById('ingredients'),
        ingredients_counter = document.getElementById('ingredients-counter'),
        method = document.getElementById('method'),
        method_counter = document.getElementById('method-counter');

    ingredients_counter.textContent = `${max_ingredients - ingredients.value.length} characters left`;
    method_counter.textContent = `${max_method - method.value.length} characters left`;

    // ingedients keypress event handler
    ingredients.addEventListener('input', function () {
        ingredients_counter.textContent = `${max_ingredients - ingredients.value.length} characters left`;
    });

    // method keypress event handler
    method.addEventListener('input', function () {
        method_counter.textContent = `${max_method - method.value.length} characters left`;
    });
});