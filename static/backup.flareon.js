var simplemde_editor;

function initialize_weekday()
{
    key = ["Sunday", "Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday"];

    date = new Date();
    $('#year-value').val(date.getFullYear());
    $('#month-value').val(date.getMonth()+1);
    $('#day-value').val(date.getDate());
    
    $('#weekday-value').text("("+key[date.getDay()]+")");    
}

function update_weekday()
{
    key = ["Sunday", "Monday", "Tuesday", "Wednesday",
           "Thursday", "Friday", "Saturday"];

    year = $('#year-value').val();
    month = $('#month-value').val();
    day = $('#day-value').val();

    date = new Date(year, month, day);
    $('#weekday-value').text("("+key[date.getDay()]+")");    
};

function deal_media_response(response)
{
    /* Append media to media holder */
    $('#media-holder').html(response['HTML']);

    /* Change total filesize */
    $('#total-filesize').html(response['FILESIZE']);

    /* Change total filenumber */
    filenum = parseInt(response['FILENUM']);
    if(filenum == 0)
    {
        $('#total-filenum').html('(0 file)');
        $('#total-filesize').css('color','#888');
        $('#total-filenum').css('color','#888');
    }
    else if(filenum == 1)
    {
        $('#total-filenum').html('(1 file)');
        $('#total-filesize').css('color','#4cae4c');
        $('#total-filenum').css('color','#4cae4c');
    }
    else
    {
        $('#total-filenum').html('('+ filenum +' files)');
        $('#total-filesize').css('color','#4cae4c');
        $('#total-filenum').css('color','#4cae4c');
    }
};

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
        success: function(response)
        {
            deal_media_response(response);
        }
    });

}


function remove_media(media_id)
{
    $.ajax({
        type: "POST",
        url: '/media/remove',
        data: {"media_id":media_id},
        success: function(response)
        {
            deal_media_response(response);
        }
    })
}

function open_file()
{
    /* Open File */
    $("#open-btn-fileholder").change(function(e)
    {
        var reader = new FileReader();

        reader.onload = function(e) {
            var data = reader.result;
            /* Convert metadata */
            metadata = data.split("---")[1];
            metadata = metadata.split("\n");

            $.each(metadata, function(index, text)
            {
                if(text.indexOf("title:") != -1)
                {
                    text = text.split(":");
                    text.shift();
                    text = text.join(":").trim();

                    if(text[0] == '"')
                    {
                        text = text.slice(1,-1);
                    }
                    $("#title-value").val(text);
                }

                else if(text.indexOf("date:") != -1)
                {
                    text = text.split(":");
                    text.shift();
                    text = text.join(":").trim();

                    text = text.split('-');
                    year = parseInt(text[0]);
                    month = parseInt(text[1]);
                    day = parseInt(text[2]);

                    if(jQuery.type(year+month+day) == "number")
                    {
                        $("#year-value").val(year);
                        $("#month-value").val(month);
                        $("#day-value").val(day);

                        update_weekday();
                    }

                }
            })

            /* Read contents */
            contents = data.split("---");
            contents.shift();
            contents.shift();
            contents = contents.join("---");
            simplemde_editor.value(contents.trim());

        }

        reader.readAsText(e.target.files[0]);
        
        /* Set filename entry */
        $("#filename").val(e.target.files[0]['name']);
    });
}


function insert_media_link(filename, url)
{
    var media_id = "![" + filename + "](" + url + ")";
    pos = simplemde_editor.codemirror.getCursor();
    simplemde_editor.codemirror.setSelection(pos, pos);
    simplemde_editor.codemirror.replaceSelection(media_id);
}


function save_file()
{
    var textToSaveAsBlob = new Blob([simplemde_editor.value()]);
    var textToSaveAsURL = window.URL.createObjectURL(textToSaveAsBlob);
    var fileNameToSaveAs = "text.flareon.md";
    var downloadLink = document.createElement("a");
    downloadLink.download = fileNameToSaveAs;
    downloadLink.innerHTML = "Download File";
    downloadLink.href = textToSaveAsURL;
    downloadLink.onclick = function(event){document.body.removeChild(event.target);};
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
 
    downloadLink.click();
}

$(document).ready(function()
{
    /* Initialize SimpleMDE Editor */
    simplemde_editor = new SimpleMDE(
    {
         element: $("#Editor")[0],
         spellChecker: false
    });

    /* Hookup Ctrl+O , Ctrl+S to Open and Save respectively */
    $(window).bind('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (String.fromCharCode(event.which).toLowerCase()) {
            case 's':
                event.preventDefault();
                alert('ctrl-s');
                break;
            case 'o':
                event.preventDefault();
                $("#open-btn").trigger("click");
                break;
            }
        }
    });

    initialize_weekday();

    /* Mock False Link */
    $("#open-btn").click(function()
    {
        $("#open-btn-fileholder").trigger("click");
    });

    /* Media Management */
    $("#add-media").click(function()
    {
        $("#fileholder").trigger("click");
    });


    /* Open file */
    open_file();

    $("#year-value").change(function() {update_weekday(); });
    $("#month-value").change(function() {update_weekday(); });
    $("#day-value").change(function() {update_weekday(); });
    
    $("#fileholder").change(function()
    {
        add_media();
    });
});
