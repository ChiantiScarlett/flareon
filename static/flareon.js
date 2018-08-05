var EDITOR; /* Global variable for Editor */
var EXPLORER_MODE = false; /* whether Explorer is open */

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
        data: {index: index},
        dataType: 'json',
        cache: false,
        success: function(response)
        {
            $('#md-title').val(response['title']);
            $('#md-filename').val(response['filename']);
            $('#md-date').val(response['date']);
            $('#md-category').val(response['category']);
            $('#md-tags').val(response['tags']);
            $('#md-dbx-sync-id').val(response['dbx_sync_id']);

            var pos = EDITOR.codemirror.getCursor();
            EDITOR.codemirror.setSelection(pos, pos);
            EDITOR.codemirror.replaceSelection(response['contents']);

            var pos = EDITOR.codemirror.getCursor();
            EDITOR.codemirror.setSelection(pos, pos);

            /* Prevent lazy loading */
            EDITOR.codemirror.replaceSelection('\n');
               
        }
    });

    $('#screen').css('display','none');
    $('#explorer-container').css('display','none');
    EXPLORER_MODE = true;
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
                alert('ctrl-s');
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
