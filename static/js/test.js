// credit ai for most of this code. i just stuck together pieces and changed the values to make it do what i want

// flash hide animation:
function hide() {
    // move above screen
    document.getElementById('flash').style.top = "-120px";
    // hide element
    setTimeout(() => {
        document.getElementById('flash').style.display='none'
    }, 500);
}

// flash appear animation:
// wait for page load
document.addEventListener("DOMContentLoaded", () => {
    const flash = document.getElementById("flash");
    // move above screen
    setTimeout(() => {
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
    // after some time automatically close
    // add a moving bar to show when it will close
    setTimeout(() => {
        hide()
    }, 7000);
});

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

// enables the 2nd delete account button when the first one is clicked to avoid accidentally deleting the account. probably temporary
function deleteconfirm() {
    const btn = document.getElementById("deleteconfirm");
    btn.removeAttribute("disabled");
}

// 
// search stuff
// 

// search input
const searchInput = document.querySelector("[content-search]")

// update on search input change
searchInput.addEventListener("input", e => {
    // convert search to lowercase
    const value = e.target.value.toLowerCase()

    const mapIsVisible = 
        searchesElement.children[0].textContent.includes(value)
    map.classList.toggle("hide", !mapIsVisible)

    const charIsVisible = 
        searchesElement.children[1].textContent.includes(value)
    char.classList.toggle("hide", !charIsVisible)

    searchesElement.children.array.forEach(element => {
        const isVisible = 
            searchesElement.children[element].textContent.includes(value)
        element.classList.toggle("hide", !isVisible)
    });
})

const searchesElement = document.querySelector("[searches]")
searchesArray = []

console.log(searchesElement.children)


function currshow() {
    document.getElementById('nextcurrency').style.display='none'
}