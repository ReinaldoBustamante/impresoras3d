
var dato = document.getElementById("colo");
dato = dato.innerHTML;
dato = dato.substring(9, 22);
if (dato == "Imprimiendo..") {
    document.getElementById("colo").style.background = "Red";
}

else {
    document.getElementById("colo").style.background = "Green";
}








