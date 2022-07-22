const searchField=document.querySelector('#Barcode');


searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if(event.keyCode === 13){
        console.log('searchValue', searchValue);


        fetch("search-barcode/", {
            body: JSON.stringify({ searchText: searchValue}),
            method: "POST",

        })
            .then((res) => res.json())
            .then((data) => {
                if(data['barcode']){
                console.log('data1', data);
                document.location.href = "#error";
                } else {
                location.reload();
                }

                });
    }
});