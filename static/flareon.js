function update_weekday()
{
    key = ["Sunday", "Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday"];

    date = new Date();
    $('#year-value').val(date.getFullYear());
    $('#month-value').val(date.getMonth()+1);
    $('#day-value').val(date.getDate());
    
    $('#weekday-value').text("("+key[date.getDay()]+")");
}

function add_media()
{
    var form_data = new FormData($('#media-upload')[0]);
    $.ajax({
        type: "POST",
        url: '/media/add',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data)
        {
            $('#media-holder').html(data);
        },
        failure: function(e)
        {
            alert('failed');
        }
    });

}

function remove_media(media_id)
{
    $.ajax({
        type: "POST",
        url: '/media/remove',
        data: {"media_id":media_id},
        success: function(data)
        {
            $('#media-holder').html(data);
        }
    })
}

$(document).ready(function()
{
    var simplemde_editor = new SimpleMDE(
    {
         element: $("#Editor")[0]
    });

    update_weekday();

    /* Media Management */
    $("#add-media").click(function()
    {

        $("#fileholder").trigger("click");
    });
    $("#fileholder").change(function()
    {
        add_media();
    });
});
