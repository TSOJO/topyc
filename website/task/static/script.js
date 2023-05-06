let TICK = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#198754" class="bi bi-check-circle-fill" viewBox="0 0 16 16">',
        '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>',
    '</svg>'
].join('')

let CROSS = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#DF4957" class="bi bi-x-circle-fill" viewBox="0 0 16 16">',
        '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>',
    '</svg>'
].join('')

function checkKeywordPresent(text, keyword) {
    text = text.replaceAll('\n', ' ')
    if (text.includes(' ' + keyword)) {
        return true;
    }
    if (text.startsWith(keyword)) {
        return true;
    }
    return false;
}

function resetRunButton() {
    $('#run-button').prop('disabled', false)
    $('#run-button').html([
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill me-1" viewBox="0 0 16 16">',
            '<path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>',
        '</svg>',
        'Run code'
    ].join(''))
}

function keywordTooltip() {
    const tooltip = bootstrap.Tooltip.getInstance('#run-button')
    tooltip.show()
}

window.onpageshow = function(event) {
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
    })
    // Initialise ACE editor.
    let editor = ace.edit('editor')
    ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
    editor.setTheme("ace/theme/textmate")
    editor.session.setMode("ace/mode/python")
    editor.session.setUseWrapMode(true)
    editor.setOptions({maxLines: 15, minLines: 15})
    
    let textarea = $('#user-code').hide()

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

    resetRunButton()

    $('#run-button').click(function() {
        if (canSubmit) {
            textarea.val(editor.getValue())
            // Disable submit button.
            $(this).prop('disabled', true)
            // Replace text with a spinner.
            $(this).html(
                '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Running...'
            )

            // Run code.
            let payload = {
                code: textarea.val(),
                // taskID: 
            }
            
            fetch('/api/run',
                {
                    method: 'POST',
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (response.status == '400') {
                        keywordTooltip()
                        resetRunButton()
                        throw new Error('Code must contain the keywords.')
                    }
                    return response.json()
                })
                .then(data => {
                    console.log(data.results)
                    let html = [
                        '<tr>',
                            '<td>' + data.time + '</td>',
                            '<td>']
                    if (data.passesOverall) {
                        html.push(TICK)
                    } else {
                        html.push(CROSS)
                    }
                    html.push(...[
                            '</td>',
                            '</tr>',
                            '<tr>',
                                '<td colspan="2">',
                                    '<table class="table mb-0">',
                                        '<thead>',
                                            '<tr>',
                                                '<th scope="col">Test #</th>',
                                                '<th scope="col">Result</th>',
                                            '</tr>',
                                        '</thead>',
                                        '<tbody>'
                    ])
                    data.results.forEach((element, index, _) => {
                        html.push(...[
                                            '<tr>',
                                                '<td>' + (index+1) + '</td>',
                                                '<td>'
                        ])
                        if (element.verdict === 'AC') {
                            html.push(TICK)
                        } else {
                            html.push(CROSS)
                        }
                        if (element.message) {
                            html.push(...[
                                '<a data-bs-toggle="modal" data-bs-target="#detail' + (index+1) + '-modal" href="#"',
                                '   class="text-decoration-none d-flex align-items-center">',
                                '   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#ff6a00" class="bi bi-exclamation-circle" viewBox="0 0 16 16">',
                                '      <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>',
                                '      <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>',
                                '   </svg>',
                                '</a>',
                                '<div class="modal fade" id="detail' + (index+1) + '-modal" tabindex="-1"',
                                '    aria-labelledby="detail' + (index+1) + '-modal-label" aria-hidden="true">',
                                '    <div class="modal-dialog">',
                                '        <div class="modal-content">',
                                '            <div class="modal-header">',
                                '                <h1 class="modal-title fs-5" id="detail' + (index+1) + '-modal-label">Details',
                                '                </h1>',
                                '                <button type="button" class="btn-close" data-bs-dismiss="modal"',
                                '                    aria-label="Close"></button>',
                                '            </div>',
                                '            <div class="modal-body">',
                                '                <div style="white-space:pre-wrap;" class="consolas">',
                                                     element.message,
                                '                </div>',
                                '            </div>',
                                '            <div class="modal-footer">',
                                '                <button type="button" class="btn btn-secondary"',
                                '                    data-bs-dismiss="modal">Close</button>',
                                '            </div>',
                                '        </div>',
                                '    </div>',
                                '</div>',
                            ])

                        }
                        html.push(...[
                                                '</td>',
                                            '</tr>',
                        ])
                    })
                    html.push(...[
                                        '</tbody>',
                                    '</table>',
                                '</td>',
                            '</tr>'
                    ])
                    $('#attempts-table-body').append(html.join(''))
                    resetRunButton()
                })
        } else {
            keywordTooltip()
        }
    })
}