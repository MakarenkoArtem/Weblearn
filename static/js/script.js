let switchMode =  document.getElementById("switchMode")
switchMode.onclick = function (){
    let theme = document.getElementById("theme")
    if (theme.getAttribute("href") == "/static/css/dark.css"){
        theme.href = "/static/css/light.css"
    } else {
        theme.href = "/static/css/dark.css"
    }
}
function test (){
    let theme = document.getElementById("theme")
    if (theme.getAttribute("href") == "/static/css/dark.css"){
        theme.href = "/static/css/light.css"
    } else {
        theme.href = "/static/css/dark.css"
    }
}