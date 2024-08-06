// datatables definitions
new DataTable('#stable', {
    order: [
        [0, 'desc']
    ]
});

new DataTable('#stable_2', {
    order: [
        [1, 'desc']
    ]
});

new DataTable('#stable_3', {
    order: [
        [1, 'desc']
    ]
});

// formatting for ride time entry
function format_time(time_input) {

    time_num = time_input.value;

    if (time_num.length == 2) {
        time_input.value = time_input.value + ":";
        return false;
    }
    if (time_num.length == 5) {
        time_input.value = time_input.value + ":";
        return false;
    }
}

// define data-href to enable clicking on data rows
$(document).on('click', '*[data-href]', function() {
    window.location = $(this).data("href");
});


// handle delete confirmation modal
let confirmButton = document.getElementById("confirmButton");
let deleteButton = document.getElementById("deleteButton");

confirmButton.addEventListener('click', function() {
    let ride_id = deleteButton.value;

    fetch('/view_ride', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "ride_id": ride_id
            }),
        })
        .then(response => {
            // check response, if ok, close modal and redirect
            if (response.ok) {
                $('#d_modal').modal('hide');
                window.location.href = '/bike_log';
            }
        });
});
