const toggleButtonF2 = document.getElementById('toggleButtonF2');
const popupF2 = document.getElementById('popupF2');

toggleButtonF2.addEventListener('click', (event) => {
    popupF2.classList.toggle('hidden');
    event.stopPropagation(); // Остановить всплытие события
});

// Закрытие окна при клике вне его
document.addEventListener('click', (event) => {
    if (!popupF2.classList.contains('hidden') && !popupF2.contains(event.target) && event.target !== toggleButtonF2) {
        popupF2.classList.add('hidden');
    }
});