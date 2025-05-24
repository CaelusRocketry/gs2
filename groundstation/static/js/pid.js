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

let offsets;

function pid_init() {
    let blocks = $("object.pid").contents().find("div > div > div");

    blocks.each(function () {
        let text = $(this).text();

        if (text.startsWith("DATA")) {
            let id = text.substring(5);
            pid_blocks[id] = this;
            $(this).css("font-size", "18px");
        }
    });
}

function sidebar_init() {
    $(".data-value").each(function () {
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

$(window).on("load", function () {
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
                    $.each(payload[sensor_type], function (id, value) {
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

function parseArr(a) {
    let rtr = { ...a }

    for (const key in rtr) {
        if (rtr[key].innerHTML == "? PSI")
            rtr[key] = 0
        else
            rtr[key] = rtr[key].innerHTML.substring(0, rtr[key].innerHTML.indexOf("PSI") != -1 ? rtr[key].innerHTML.indexOf("PSI") : 1)

        rtr[key] = parseInt(rtr[key])
    }

    return rtr
}

document.getElementById('zero').addEventListener('click', () => {
    document.getElementById('zero').disabled = true;
    document.getElementById('zero').innerHTML = "Collecting Data"


    offsets = { ...sidebar_blocks };
    offsets = parseArr(offsets);

    let count = 1;

    let interval = setInterval(() => {
        count++;

        let newVals = { ...sidebar_blocks };
        newVals = parseArr(newVals);

        for (const key in newVals)
            offsets[key] += newVals[key];

        if (count >= 10) {
            for (const key in offsets)
            {
                offsets[key] /= count;
                offsets[key] = parseInt(offsets[key])
            }

            $.ajax({
                type: "GET",
                url: '/zeroall',
                data: {
                    "result": JSON.stringify(offsets),
                },
                dataType: "json",
                success: function (data) {
                    // alert("successfull")
                },
                failure: function () {
                    // alert("failure");
                }
            });

            document.getElementById('zero').disabled = false;
            document.getElementById('zero').innerHTML = "Zero Sensors";

            document.getElementById('offsets').innerHTML = '';
            let o = '<span>Offsets</span>';
            for (const key in offsets) {
                if(key == 'PT-1' || 'PT-2' || 'PT-3' || 'PT-4')
                    o += `<div class='offset'><span>${key}: ${offsets[key]}</span></div>`;
            }
            document.getElementById('offsets').innerHTML = o;

            clearInterval(interval);
        }
    }, 500);
});