function HTMLTick(tooltipText) {
    return [
        '<span>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#198754" class="bi bi-check-circle-fill" viewBox="0 0 16 16" data-bs-toggle="tooltip" data-bs-title="' + tooltipText + '">',
                '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>',
            '</svg>',
        '</span>'
    ].join('')
}

function HTMLCross(tooltipText) {
    return [
        '<span>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#DF4957" class="bi bi-x-circle-fill" viewBox="0 0 16 16" data-bs-toggle="tooltip" data-bs-title="' + tooltipText + '">',
                '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>',
            '</svg>',
        '</span>'
    ].join('')
}

function getLongVerdict(verdict) {
    switch (verdict) {
        case 'AC':
            return 'Correct!'
        case 'WA':
            return 'Wrong Answer'
        case 'TLE':
            return 'Time Limit Exceeded'
        case 'MLE':
            return 'Memory Limit Exceeded'
        case 'RE':
            return 'Runtime Error'
        case 'CE':
            return 'Compilation Error'
        case 'SE':
            return 'System Error'
        case 'WJ':
            return 'Waiting for Judge'
        default:
            return 'Unknown Error'
    }
}

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

function resetSubmitButton() {
    $('#submit-button').prop('disabled', false)
    $('#submit-button').html([
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill me-1" viewBox="0 0 16 16">',
            '<path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>',
        '</svg>',
        'Submit code'
    ].join(''))
}

function keywordTooltip() {
    const tooltip = bootstrap.Tooltip.getInstance('#submit-button')
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

    resetSubmitButton()

    $('#submit-button').click(function() {
        if (canSubmit) {
            textarea.val(editor.getValue())
            // Disable submit button.
            $(this).prop('disabled', true)
            // Replace text with a spinner.
            $(this).html(
                '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Submitting...'
            )

            // Submit code.
            let payload = {
                code: textarea.val(),
                taskID: $(this).data('task-id')
            }
            
            fetch('/api/submit-code',
                {
                    method: 'POST',
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (response.status == '400') {
                        keywordTooltip()
                        resetSubmitButton()
                        throw new Error('Code must contain the keywords.')
                    }
                    return response.json()
                })
                .then(data => {
                    let html = [
                        '<tr>',
                            '<td>' + data.time + '</td>',
                            '<td>']
                    if (data.overallVerdict == 'AC') {
                        html.push(HTMLTick(getLongVerdict(data.overallVerdict)))
                    } else {
                        html.push(HTMLCross(getLongVerdict(data.overallVerdict)))
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
                                                '<th>' + (index+1) + '</th>',
                                                '<td class="d-flex align-items-center">'
                        ])
                        if (element.verdict === 'AC') {
                            html.push(HTMLTick(getLongVerdict(element.verdict)))
                        } else {
                            html.push(HTMLCross(getLongVerdict(element.verdict)))
                        }
                        if (element.message) {
                            // Error messages.
                            html.push(...[
                                '<a data-bs-toggle="modal" data-bs-target="#detail' + (index+1) + '-modal" href="#"',
                                '   class="text-decoration-none ms-2">',
                                '   Details',
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
                    // Reinitialise tooltips.
                    $('[data-bs-toggle="tooltip"]').tooltip()
                    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
                        $(this).tooltip('hide')
                    })
                    resetSubmitButton()
                })
        } else {
            keywordTooltip()
        }
    })
}