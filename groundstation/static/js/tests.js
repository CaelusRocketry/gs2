$(function() {
    $(".delete-btn").on("click", function() {
        let test_item = $(this).parent().parent();
        let test_pk = test_item.attr("id").substring(5); // test-#

        dialog(
            `Delete Test #${test_pk}`, 
            "Are you sure you want to delete this test? This action is irreversible!",
            function() {
                $.post(`/delete_test/${test_pk}`, function() {
                    test_item.remove();
                    if ($("#test-list").children().length === 0) {
                        $("#test-list").append("<span id=\"no-items\">No tests found.</span>")
                    }
                }).fail(function() {
                    // TODO: remove this or add custom alert method
                    alert("Failed to delete test!");
                })
            });
    })

    $(".export-btn").on("click", function() {
        // since disabled prop isn't supported for a tags
        if ($(this).attr("disabled")) 
            return false;
    })
});