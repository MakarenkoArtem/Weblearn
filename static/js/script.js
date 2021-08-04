let switchMode = document.getElementById("switchMode");
switchMode.onclick = function () {
    let theme = document.getElementById("theme");
    if (theme.getAttribute("href") == "/static/css/dark.css") {
        theme.href = "/static/css/light.css";
    } else {
        theme.href = "/static/css/dark.css";
    }
}

function test() {
    let theme = document.getElementById("theme");
    /*alert("Error");     так можно выводить сообщения*/
    if (theme.getAttribute("href") == "/static/css/dark.css") {
        theme.href = "/static/css/light.css";
        localStorage.setItem("theme", "light");
    } else {
        theme.href = "/static/css/dark.css";
        localStorage.setItem("theme", 'dark');
    }
    console.log(`New theme: ${localStorage.getItem("theme")}`);
}

function init() {
    let theme = document.getElementById("theme");
    console.log(`Theme: ${localStorage.getItem("theme")}`);
    if (localStorage.getItem("theme") === "dark") {
        theme.href = "/static/css/dark.css";
        console.log(localStorage.setItem("theme"));
        localStorage.setItem("theme", 'dark');
    }
}