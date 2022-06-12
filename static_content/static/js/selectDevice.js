const select=document.querySelector('.form-select')

function getval(){
    var x = document.getElementById("selectDevice").value;
    console.log (x)
fetch("/accounts/devices/current-device/", {
    body: JSON.stringify({id_changeDevice: x}),
    method: "POST",
    })


setTimeout(function(){ location.reload() }, 1000)

}






fetch("/accounts/devices/list-devices/", {
            method: "POST",
        })
    .then((res) => res.json())
    .then((data) => {
    console.log('devices_list', data);

    data.forEach((item) => {
        var selected=""
        if(item.current==true){
            selected="selected"
        }

        select.innerHTML += `
            <option name="changed" value=${item.id} ${selected} >${item.pseudonym} </option>
            `;

        });
});