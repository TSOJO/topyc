function checkKeywordPresent(text, keyword) {
    if (text.includes(' ' + keyword + ' ')) {
        return true;
    }
    if (text.startsWith(keyword + ' ')) {
        return true;
    }
    if (text.endsWith(' ' + keyword)) {
        return true;
    }
    return false;
}

window.onpageshow = function(event) {
    let editor = ace.edit('editor')
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    editor.setTheme("ace/theme/textmate")
    editor.session.setMode("ace/mode/python")
    editor.session.setUseWrapMode(true)
    editor.setOptions({maxLines: 15, minLines: 15})
    
    let textarea = $('textarea[name="user-code"]').hide()

    // If a keyword has not been used, we don't let the student submit.
    let canSubmit = false
    editor.on('change', () => {
        // Update the hidden textarea with the value in the front-end editor.
        textarea.val(editor.getValue())

        canSubmit = true
        $('#keywords').children().each((_, child) => {
            let keyword = $(child).data('keyword')
            if (checkKeywordPresent(textarea.val(), keyword)) {
                $(child).addClass('list-group-item-success')
            } else {
                $(child).removeClass('list-group-item-success')
                canSubmit = false
            }
        })
    })

    $('#run-button').prop('disabled', false)
    $('#run-button').html([
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill me-1" viewBox="0 0 16 16">',
            '<path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>',
        '</svg>',
        'Run code'
    ].join(''))

    $('#run-button').click(function() {
        if (canSubmit) {
            textarea.val(editor.getValue())
            // Disable submit button.
            $(this).prop('disabled', true)
            // Replace text with a spinner.
            $(this).html(
                '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Running...'
            )
            // Submit form.
            $('#code-form').submit()
        } else {
            alert('probably display a warning of some kind....')
        }
    })
}