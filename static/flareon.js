var EDITOR; /* Global variable for Editor */
var EXPLORER_MODE = false; /* whether Explorer is open */

function validate_date()
{
    $.ajax({
        type: "POST",
        url: '/validate/date',
        data: {'date': $('#md-date').val()},
        dataType: 'json',
        cache: false,
        success: function(response)
        {
            $('#md-date').val(response['date']);
            $('#md-date-wd').text(response['weekday']);
        }
    });
}


function open_explorer()
{
    $.ajax({
        type: "POST",
        url: '/load/localfiles',
        contentType: false,
        cache: false,
        processData: false,
        success: function(HTML)
        {
            $('#explorer-files').html(HTML);
        }
    });

    $('#screen').css('display','inline');
    $('#explorer-container').css('display','inline');
    EXPLORER_MODE = true;
}

function close_explorer()
{
    $('#screen').css('display', 'none');
    $('#explorer-container').css('display', 'none');
    EXPLORER_MODE = false;
}

function load_md_file(index)
{
    $.ajax({
        type: "POST",
        url: '/load/mdfile',
        data: {'index': index},
        dataType: 'json',
        cache: false,
        success: function(response)
        {
            $('#md-filename').val(response['data']['filename']);
            $('#md-title').val(response['data']['title']);
            $('#md-filename').val(response['data']['filename']);
            $('#md-date').val(response['data']['date']);
            $('#md-category').val(response['data']['category']);
            $('#md-tags').val(response['data']['tags']);
            $('#md-dbx-sync-id').val(response['data']['dbx_sync_id']);

            EDITOR.codemirror.setValue(response['data']['contents']);


            var pos = EDITOR.codemirror.getCursor();
            EDITOR.codemirror.setSelection(pos, pos);
            EDITOR.codemirror.replaceSelection('');

            $('#dbx-files').html(response['templates']);
            $('#dbx-filesinfo').val(response['folder_volume']);
        }
    });

    $('#screen').css('display','none');
    $('#explorer-container').css('display','none');
    EXPLORER_MODE = true;
}


function save_md_file()
{
    $.ajax({
        type: "POST",
        url: '/save/mdfile',
        data: {
            'filename': $('#md-filename').val(),
            'title': $('#md-title').val(),
            'category': $('#md-category').val(),
            'date': $('#md-date').val(),
            'tags': $('#md-tags').val(),
            'dbx_sync_id': $('#md-dbx-sync-id').val(),
            'contents': EDITOR.value()
        },
        dataType: 'json',
        cache: false,
        success: function(response)
        {
            if(response['status'] == true)
            {
                console.log(response)
                $('#md-filename').val(response['filename'])
            }
        }
    });
}


function add_dbx_file()
{
    var form_data = new FormData($('#dbx-file-upload-form')[0]);
    $.ajax({
        type: "POST",
        url: '/dropbox/add',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(response)
        {
            if(response['status'] == true)
            {
                $('#dbx-files').html(response['templates']);
                $('#dbx-filesinfo').val(response['folder_volume']);
                $('#md-dbx-sync-id').val(response['dbx_sync_id']);
            }
        }
    });
    $('#dbx-file-upload').val("");

};

function remove_dbx_file(filename)
{
    $.ajax({
        type: "POST",
        url: '/dropbox/remove',
        data: {'filename': filename},
        dataType: 'json',
        cache: false,
        success: function(response)
        {
            if(response['status'] == true)
            {
                $('#dbx-files').html(response['templates']);
                $('#dbx-filesinfo').val(response['folder_volume']);
                $('#md-dbx-sync-id').val(response['dbx_sync_id']);
            }
        }
    });
};

function create_dbx_file_link(filename)
{
    $.ajax({
        type: "POST",
        url: '/dropbox/createlink',
        data: {'filename': filename},
        dataType: 'json',
        cache: false,
        success: function(response)
        {
            if(response['status'] == true)
            {
                var pos = EDITOR.codemirror.getCursor();
                EDITOR.codemirror.setSelection(pos, pos);
                EDITOR.codemirror.replaceSelection(response['link']);
            }
        }
    });
}


$(document).ready(function()
{
    /* Initialize SimpleMDE Editor */
    EDITOR = new SimpleMDE(
    {
         element: $("#Editor")[0],
         spellChecker: false,
         autoDownloadFontAwesome: false
    });

    /* Hookup Ctrl+O , Ctrl+S to Open and Save respectively */
    $(window).bind('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (String.fromCharCode(event.which).toLowerCase()) {
            case 's':
                event.preventDefault();
                save_md_file();
                break;
            case 'o':
                event.preventDefault();
                open_explorer();
                break; 
            }
        }
    });

    /* Close explorer when ESC is pressed. */
    $(window).bind('keydown', function(event) {
        if (event.keyCode == 27 && EXPLORER_MODE)
            close_explorer();
    });

});
