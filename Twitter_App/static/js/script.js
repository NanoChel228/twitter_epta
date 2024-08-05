const modal = document.getElementById('modal');
const btn = document.getElementById('open-modal');
const img = document.getElementsByClassName('close-modal')[0];

btn.onclick = function(){
    modal.style.display = "flex";
}
img.onclick = function(){
    modal.style.display = "none";
}
window.onclick = function(event){
    if (event.target === modal) {
        modal.style.display = "none";
    }
};