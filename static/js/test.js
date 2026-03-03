// credit ai

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

function swapCSS() {
    const current = document.getElementById("theme").getAttribute("href");
    current == "/static/css/style_dark.css" 
    ? document.getElementById("theme").href = '/static/css/style_light.css'
    : document.getElementById("theme").href = '/static/css/style_dark.css'
}



// copilot

// Load saved theme on page load
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        document.getElementById("theme").href = savedTheme;
    }
});

function toggleTheme() {
    const link = document.getElementById("theme");
    const current = link.getAttribute("href");

    const dark = "/static/css/style_dark.css";
    const light = "/static/css/style_light.css";

    const newTheme = current === dark ? light : dark;

    link.href = newTheme;
    localStorage.setItem("theme", newTheme);
}
