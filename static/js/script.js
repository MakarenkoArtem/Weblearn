let switchMode = document.getElementById("switchMode")
switchMode.onclick = function () {
    let theme = document.getElementById("theme")
    if (theme.getAttribute("href") == "/static/css/dark.css") {
        theme.href = "/static/css/light.css"
    } else {
        theme.href = "/static/css/dark.css"
    }
}

function test() {
    let theme = document.getElementById("theme")
    console.log(localStorage.getItem("theme"))
    if (theme.getAttribute("href") == "/static/css/dark.css") {
        theme.href = "/static/css/light.css"
        localStorage.removeItem("theme")
    } else {
        theme.href = "/static/css/dark.css"
        localStorage.setItem("theme", 'dark')
    }
}

function init() {
    let theme = document.getElementById("theme")
    console.log(localStorage.getItem("theme"))
    if (localStorage.getItem("theme") !== null) {
        theme.href = "/static/css/dark.css"
        localStorage.setItem("theme", 'dark')
    }
}