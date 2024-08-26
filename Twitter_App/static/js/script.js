const openButtons = document.querySelectorAll('[id^="open-modal"]');
const closeButtons = document.querySelectorAll('.close-modal');

openButtons.forEach(button => {
    button.onclick = function() {
        const modalId = button.getAttribute('data-modal');
        document.getElementById(modalId).style.display = "flex";
    }
});

closeButtons.forEach(button => {
    button.onclick = function() {
        const modalId = button.getAttribute('data-modal');
        document.getElementById(modalId).style.display = "none";
    }
});

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
};
function update_input_image(e){
    console.log(e.files[0]);
}