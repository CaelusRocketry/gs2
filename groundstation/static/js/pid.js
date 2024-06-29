let data = {
    "PT-1": null,
    "PT-2": null,
    "PT-3": null,
    "PT-4": null,
    "TC-1": null,
    "LC-1": null,
    "LC-2": null,
    "LC-3": null,
}

function initializePID() {
    let divs = $("object.pid").contents().find("div > div > div");
    for (let i = 0; i < divs.length; i++) {
        text = $(divs[i]).text();
        if (text.startsWith("DATA")) {
            let identifier = text.split(" ")[1];
            data[identifier] = divs[i];
            $(divs[i]).css({
                color: "red",
                fontWeight: "bold",
                fontSize: "18px",
            })
        }
    }
    console.log(data);
}

function updatePID(identifier, value) {
    if (data[identifier] != null) {
        let unit = "PSI";
        if (identifier.startsWith("LC")) 
            unit = "N";
        else if (identifier.startsWith("TC"))
            unit = "°F";
        $(data[identifier]).text(value + " " + unit);
    }
}

$(function() {
    setTimeout(function() {
        initializePID();
    }, 100);
});