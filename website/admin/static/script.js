$('.user-group-select').change((e) => {
    e.target.form.submit()
})

window.onpageshow = () => {
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
    })
    
    // Initialise code editor.
    let editor = ace.edit('editor')
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    editor.setTheme("ace/theme/textmate")
    editor.session.setMode("ace/mode/python")
    editor.session.setUseWrapMode(true)
    editor.setOptions({ readOnly: true, highlightActiveLine: false, highlightGutterLine: false, maxLines: Infinity })
    editor.renderer.$cursorLayer.element.style.display = "none"
}
