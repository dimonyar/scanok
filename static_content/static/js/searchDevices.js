const searchField=document.querySelector('#searchField');
const tableOutput=document.querySelector('.table-output');
const appTable=document.querySelector('.app-table');
tableOutput.style.display='none';
const tbody=document.querySelector('.table-body')

function cl(){
    var radio = document.getElementsByName('current');

    for (var i=0; i<radio.length; i++) {
        radio[i].onchange = currentDevice;
    }
}

function currentDevice() {
    console.log (this.value);
fetch("/accounts/devices/current-device/", {
    body: JSON.stringify({id_changeDevice: this.value}),
    method: "POST",
    })
}



searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if(searchValue.trim().length>3){
        tbody.innerHTML = "";
        console.log('searchValue', searchValue);

        fetch("search-devices/", {
            body: JSON.stringify({ searchText: searchValue}),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log('data', data);

                appTable.style.display='none';

                tableOutput.style.display='block';


                       data.forEach((item) => {
                        var checked=""
                        if(item.current==true){
                            checked="checked"
                        }

                        var day = new Date(item.created).toLocaleDateString();
                        tbody.innerHTML += `
                            <tr>
                                <td>${item.name}</td>
                                <td>${item.pseudonym}</td>
                                <td>${day}</td>
                                <td><input type="radio" name="current"  value=${item.id} onclick="cl()" ${checked}></td>
                                <td>
                                    <div class="dropdown">
                                        <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton2"
                                                data-bs-toggle="dropdown" aria-expanded="false"></button>
                                        <ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="dropdownMenuButton2">
                                            <li><a class="dropdown-item active"
                                                   href="#">Detail</a></li>
                                            <li><a class="dropdown-item" href="/accounts/devices/update/${item.id}">Edit</a></li>
                                            <li><a class="dropdown-item" href="/accounts/devices/delete/${item.id}">Delete</a>
                                            </li>
                                        </ul>
                                    </div>
                                </td>
                            </tr>`;

                    });


            });
    }

    else{
        tableOutput.style.display='none';
        appTable.style.display='block';

    }

});