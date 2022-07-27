function cl(){
    var radio = document.getElementsByName('hold');

    for (var i=0; i<radio.length; i++) {
        radio[i].onchange = doc_hold;
    }
}

function doc_hold() {
    console.log (this.value);
    fetch("doc_hold/", {
        body: JSON.stringify({id_changeDoc: this.value}),
        method: "POST",
        })
    }