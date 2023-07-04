function checkKeywordPresent(text, keyword) {
    text = text.replaceAll('\n', ' ')
    keywordNoSpaces = keyword.replaceAll(' ', '')
    if (text.includes(keyword) || text.includes(keywordNoSpaces)) {
        return true;
    }
    return false;
}

function checkAllKeywordsPresent() {
    if ($('#keywords').length) {  // exists
        let res = true
        $('#keywords').children().each((_, child) => {
            let keyword = String($(child).data('keyword'))
            if (checkKeywordPresent($('#user-code').val(), keyword)) {
                $(child).addClass('list-group-item-success')
            } else {
                $(child).removeClass('list-group-item-success')
                res = false
            }
        })
        return res
    }
    return true
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

window.onpageshow = () => {
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
    })

    try {
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
            canSubmit = checkAllKeywordsPresent()
        })
    
        resetSubmitButton()
    
        $('#submit-button').unbind('click').click(function() {
            canSubmit = checkAllKeywordsPresent()
            if (canSubmit) {
                textarea.val(editor.getValue())
                // Disable submit button.
                $(this).prop('disabled', true)
                // Replace text with a spinner.
                $(this).html(
                    '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Submitting...'
                )
                let code = textarea.val()
    
                // Submit code.
                let payload = {
                    code: code,
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
                        let row_number = $('#attempts-table-body').children().length + 1
                        let html = [
                            '<tr class="d-flex">',
                                '<th scope="row" class="col-4">' + data.time + '</th>',
                                '<td class="col-6 d-flex flex-wrap justify-content-start align-items-center" style="gap:5px;">']
                        data.results.forEach((element, index, _) => {
                            if (element.verdict === 'AC') {
                                html.push(HTMLTick(getLongVerdict(element.verdict)))
                            } else if (element.verdict === 'WA') {
                                html.push(HTMLCross(getLongVerdict(element.verdict)))
                            } else {
                                if (element.message) {
                                    html.push(...[
                                        '<div class="modal fade" id="detail' + row_number + '-' + (index+1) + '-modal" tabindex="-1"',
                                        '    aria-labelledby="detail' + row_number + '-' + (index+1) + '-modal-label" aria-hidden="true">',
                                        '    <div class="modal-dialog">',
                                        '        <div class="modal-content">',
                                        '            <div class="modal-header">',
                                        '                <h1 class="modal-title fs-5" id="detail' + row_number + '-' + (index+1) + '-modal-label">Details',
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
                                        '<a data-bs-toggle="modal" data-bs-target="#detail' + row_number + '-' + (index+1) + '-modal" href="#">',
                                    ])
                                }
                                html.push(HTMLBang(getLongVerdict(element.verdict)))
                                if (element.message) {
                                    html.push(...[
                                        '</a>'
                                    ])
                                }
                            }
                        })
                        html.push(...[
                                '</td>',
                                '<td class="col-2 d-flex justify-content-between align-items-center">'
                        ])
                        if (data.overallVerdict == 'AC') {
                            html.push(HTMLTick(getLongVerdict(data.overallVerdict)))
                        } else if (data.overallVerdict == 'WA') {
                            html.push(HTMLCross(getLongVerdict(data.overallVerdict)))
                        } else {
                            html.push(HTMLBang(getLongVerdict(data.overallVerdict)))
                        }
                        html.push(...[
                                    '<div class="modal fade" id="code' + row_number + '-modal" tabindex="-1" aria-labelledby="code' + row_number + '-modal-label" aria-hidden="true">',
                                        '<div class="modal-dialog">',
                                            '<div class="modal-content">',
                                                '<div class="modal-header">',
                                                    '<h1 class="modal-title fs-5" id="code' + row_number + '-modal-label">Code</h1>',
                                                    '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                                                '</div>',
                                                '<div class="modal-body">',
                                                    '<div style="white-space:pre-wrap;" class="consolas">' + code + '</div>',
                                                '</div>',
                                                '<div class="modal-footer">',
                                                    '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>',
                                                '</div>',
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<a data-bs-toggle="modal" data-bs-target="#code' + row_number + '-modal" href="#">',
                                        '<span>',
                                            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-fill" viewBox="0 0 16 16">',
                                                '<path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>',
                                                '<path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"/>',
                                            '</svg>',
                                        '</span>',
                                    '</a>'
                        ])
                        html.push(...[
                                '</td>',
                            '</tr>'
                        ])
                        $('#attempts-table-body').prepend(html.join(''))
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
    catch {}
}