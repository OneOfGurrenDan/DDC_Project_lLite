// JavaScript для формы рецептуры

document.addEventListener('DOMContentLoaded', function() {
    console.log('Recipe form script loaded');
    
    // Пример: динамическое добавление реагентов
    const addIngredientBtn = document.querySelector('.btn-add-ingredient');
    
    if (addIngredientBtn) {
        addIngredientBtn.addEventListener('click', function() {
            console.log('Add ingredient clicked');
            // Здесь можно добавить логику для динамического добавления полей
        });
    }
});


