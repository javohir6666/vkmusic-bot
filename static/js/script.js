// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    const taskCards = document.querySelectorAll('.task-card');

    taskCards.forEach(card => {
        card.addEventListener('click', function() {
            alert(`You selected: ${this.textContent}`);
        });
    });
});
