// flash appear animation:
const flash = document.getElementById("flash");
// move above screen
setTimeout(() => {
    // flash.style.transition = "all 0s";
    flash.style.top = "-120px";
}, 0);

// make visable
setTimeout(() => {
    flash.style.display='';
}, 70);

// move down
setTimeout(() => {
    flash.style.top = "0px";
}, 80);

// flash hide animation
function hide() {
    // move above screen
    document.getElementById('flash').style.top = "-120px";
    // hide element
    setTimeout(() => {
        document.getElementById('hide').style.display='none'
    }, 500);
    
}

