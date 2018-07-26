function update_weekday()
{
    key = ["Sunday", "Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday"];

    weekday = new Date(
        $('#year-value').val(),
        $('#month-value').val(),
        $('#day-value').val()).getDay();
    $('#weekday-value').text("("+key[weekday]+")");
}


$(document).ready(function()
{
    var simplemde_editor = new SimpleMDE(
    {
         element: $("#Editor")[0]
    });

    $('#year-value').change(function(){update_weekday()});
});