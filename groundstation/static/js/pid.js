let pidBlocks = {
    "PT-1": null,
    "PT-2": null,
    "PT-3": null,
    "PT-4": null,
    "TC-1": null,
    "LC-1": null,
    "LC-2": null,
    "LC-3": null,
};

let sidebarBlocks = {
    "PT-1": null,
    "PT-2": null,
    "PT-3": null,
    "PT-4": null,
    "TC-1": null,
    "LC-1": null,
    "LC-2": null,
    "LC-3": null,
};

function pidInit() {
    let blocks = $("object.pid").contents().find("div > div > div");
    
    blocks.each(function() {
        let text = $(this).text();
    
        if (text.startsWith("DATA")) {
            let id = text.substring(5);
            pidBlocks[id] = this;
            $(this).css("font-size", "18px");
        }
    });
}

function sidebarInit() {
    $(".data-value").each(function() {
        let id = this.id;
        sidebarBlocks[id] = this;
    });
}

function updateData(id, value) {
    if (pidBlocks[id] == null || sidebarBlocks[id] == null) return;

    let unit = "PSI";
    if (id.startsWith("LC"))
        unit = "N";
    else if (id.startsWith("TC"))
        unit = "°F";

    $([pidBlocks[id], sidebarBlocks[id]]).text(`${value} ${unit}`);
}

$(window).on("load", function() {
    pidInit();
    sidebarInit();

    let socket = new WebSocket(`ws://${window.location.host}/data/`);

    socket.onmessage = (event) => {
        let data = JSON.parse(event.data);
        
        let header = data.header;
        let payload = data.payload;

        switch (header) {
            case "sensor_data":
                for (const sensor_type of ["pressure", "load", "thermocouple"]) {
                    $.each(payload[sensor_type], function(id, value) {
                        updateData(id, value);
                    });
                } 
                break;
            case "valve_data":
                // TODO: finish valve updating once valve data can be read
                break;
        }
    }
});
