const searchField=document.querySelector('#searchField');
const tableOutput=document.querySelector('.table-output');
const appTable=document.querySelector('.app-table');
const pagination=document.querySelector('#Page_navigator')
tableOutput.style.display='none';
const tbody=document.querySelector('.table-body')

const zeroLength = 6;


searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if(searchValue.trim().length>3){
        tbody.innerHTML = "";
        console.log('searchValue', searchValue);

        fetch("search-goods/", {
            body: JSON.stringify({ searchText: searchValue}),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log('data', data);

                appTable.style.display='none';
                pagination.style.display='none';


                tableOutput.style.display='block';


                       data.forEach((item) => {

                        tbody.innerHTML += `
                              <tr class="clickable collapsed" data-toggle="collapse" data-target="#${item.GoodF}_"
                    aria-expanded="false" aria-controls="${item.GoodF}_">
                    <td align="right">${item.GoodF.padStart(zeroLength, '0')}</td>
                    <td align="left">${item.Name}</td>
                    <td align="center">${item.Unit}</td>
                    <td align="right">${item.Price}</td>
                    <td width="10" align="center">
                        <div class="dropdown">
                            <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton2"
                                    data-bs-toggle="dropdown" aria-expanded="false"></button>
                            <ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="dropdownMenuButton2">
                                <li><a class="dropdown-item" href="/scanok/goods/update/${item.id}">Edit</a>
                                </li>
                                <li><a class="dropdown-item" href="/scanok/goods/delete/${item.id}">Delete</a>
                                </li>
                            </ul>
                        </div>
                    </td>
                </tr>

                <tbody id="${item.GoodF}_" class="collapse">
                    <tr class="box collapse" id="${item.GoodF}_">
                        <td colspan="5" style="padding:0">
                            <table class="table table-striped table-dark">
                                <thead>
                                    <tr>
                                        <th>GoodF</th>
                                        <th>Code</th>
                                        <th>BarcodeName</th>
                                        <th>Count</th>
                                    </tr>
                                </thead>
                                <tbody class='barcodes_${item.GoodF}'></tbody>`


                                const barcodes=document.querySelector('.barcodes_'+ item.GoodF)

                                item.Barcode.forEach((bar) => {
                                     barcodes.innerHTML +=`
                                     <tr>
                                        <td>${bar.GoodF}</td>
                                        <td>${bar.Code}</td>
                                        <td>${bar.BarcodeName}</td>
                                        <td>${bar.Count}</td>
                                     </tr>`
                                });

                                `</table>
                        </td>
                    </tr>
                </tbody>`;

                    });


            });
    }

    else{
        tableOutput.style.display='none';
        appTable.style.display='block';
        pagination.style.display='block';

//        location. reload()
    }

});