// credit ai for most of this code. i just stuck together pieces and changed values to make it do what i want

// flash appear animation:
document.addEventListener("DOMContentLoaded", () => {
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
});

// flash hide animation:
function hide() {
    // move above screen
    document.getElementById('flash').style.top = "-120px";
    // hide element
    setTimeout(() => {
        document.getElementById('flash').style.display='none'
    }, 500);
}

// swap theme css on click: (unused)
function swapCSS() {
    // get current theme
    const current = document.getElementById("theme").getAttribute("href");
    // if current theme is dark
    current == "/static/css/style_dark.css" 
    // if true change to light
    ? document.getElementById("theme").href = '/static/css/style_light.css'
    // if false change to dark
    : document.getElementById("theme").href = '/static/css/style_dark.css'
}

// Load saved theme on page load:
document.addEventListener("DOMContentLoaded", () => {
    // read the theme saved to local storage
    const savedTheme = localStorage.getItem("theme");
    // if there is a saved theme
    if (savedTheme) {
        // set theme to saved theme
        document.getElementById("theme").href = savedTheme;
    }
});

// swap theme css on click:
function toggleTheme() {
    // save the element and get current theme
    const link = document.getElementById("theme");
    const current = link.getAttribute("href");
    // if current theme is dark
    const newTheme = current === "/static/css/style_dark.css" 
    // if true set new theme to light
    ? "/static/css/style_light.css"
    // if false set new theme to dark
    : "/static/css/style_dark.css";
    // change the theme
    link.href = newTheme;
    // save the theme to local storage
    localStorage.setItem("theme", newTheme);
    
    // figure out how to use localStorage for remembering user? or use cookies instead?
}
