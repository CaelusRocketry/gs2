let pid_blocks = {
    "PT-1": null,
    "PT-2": null,
    "PT-3": null,
    "PT-4": null,
    "TC-1": null,
    "LC-1": null,
    "LC-2": null,
    "LC-3": null,
};

let sidebar_blocks = {
    "PT-1": null,
    "PT-2": null,
    "PT-3": null,
    "PT-4": null,
    "TC-1": null,
    "LC-1": null,
    "LC-2": null,
    "LC-3": null,
};

function pid_init() {
    let blocks = $("object.pid").contents().find("div > div > div");
    
    blocks.each(function() {
        let text = $(this).text();
    
        if (text.startsWith("DATA")) {
            let id = text.substring(5);
            pid_blocks[id] = this;
            $(this).css("font-size", "18px");
        }
    });
}

function sidebar_init() {
    $(".data-value").each(function() {
        let id = this.id;
        sidebar_blocks[id] = this;
    });
}

function update_data(id, value) {
    if (pid_blocks[id] == null || sidebar_blocks[id] == null) return;

    let unit = "PSI";
    if (id.startsWith("LC"))
        unit = "N";
    else if (id.startsWith("TC"))
        unit = "°F";

    $([pid_blocks[id], sidebar_blocks[id]]).text(`${value} ${unit}`);
}

$(window).on("load", function() {
    pid_init();
    sidebar_init();

    let socket = new WebSocket(`ws://${window.location.host}/data/`);

    socket.onmessage = (event) => {
        let data = JSON.parse(event.data);
        
        let header = data.header;
        let payload = data.payload;

        switch (header) {
            case "sensor_data":
                for (const sensor_type of ["pressure", "load", "thermocouple"]) {
                    $.each(payload[sensor_type], function(id, value) {
                        update_data(id, value);
                    });
                } 
                break;
            case "valve_data":
                // TODO: finish valve updating once valve data can be read
                break;
        }
    }
});

document.getElementById('zero').addEventListener('click', () => { // for sensor zero button
    values = { ...sidebar_blocks }; // makes copy of dict instead of referencing it directly

    for(const key in values) // remvoes the "? PSI" from the html and makes it into an int
    {
        if(values[key].innerHTML == "? PSI")
            values[key] = 0
        else
            values[key] = values[key].innerHTML.substring(0, values[key].innerHTML.indexOf("PSI") != -1 ? values[key].innerHTML.indexOf("PSI") : 1)

        values[key] = parseInt(values[key])
    }


    $.ajax({ // sent values to backend
        type: "GET",
        url: '/zeroall',
        data: {
            "result": JSON.stringify(values),
        },
        dataType: "json",
        success: function (data) {
            // any process in data
            alert("successfull")
        },
        failure: function () {
            alert("failure");
        }
    });
});
