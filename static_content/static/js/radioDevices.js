function cl(){
    var radio = document.getElementsByName('current');

    for (var i=0; i<radio.length; i++) {
        radio[i].onchange = currentDevice;
    }
}

function currentDevice() {
    console.log (this.value);
fetch("current-device/", {
    body: JSON.stringify({id_changeDevice: this.value}),
    method: "POST",
    })
}