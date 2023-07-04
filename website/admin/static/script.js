try {
    $('.user-group-select').change(e => {
        e.target.form.submit()
    })
}
catch (e) {}

try {
    $('.admin-check').change(e => {
        e.target.form.submit()
    })
}
catch (e) {}

try {
    $('#description').on('input', () => {
        $('#description-md')[0].mdContent = $('#description').val()
    })
}
catch (e) {}

try {
    $('.get-submissions').on('click', e => {
        // `e.target` would point to the <path> tag that the user clicked on which triggered the event.
        // `e.currentTarget` points to the <a> tag where the event listener has been attached.
        let userID = $(e.currentTarget).data('user-id')
        let taskID = $(e.currentTarget).data('task-id')

        spinner('#submissions-' + userID + '-' + taskID)

        fetch('/api/get-submissions/' + userID + '/' + taskID)
            .then(response => response.json())
            .then(json => {
                html = []
                for (submission of json.submissions) {
                    html.push(...[
                        '<tr>',
                        '   <th scope="row">',
                                submission.timeSubmitted,
                        '   </th>',
                        '   <td>',
                    ])
                    if (submission.overallVerdict == 'AC') {
                        html.push(HTMLTick(getLongVerdict(submission.overallVerdict)))
                    } else if (submission.overallVerdict === 'WA') {
                        html.push(HTMLCross(getLongVerdict(submission.overallVerdict)))
                    } else {
                        html.push(HTMLBang(getLongVerdict(submission.overallVerdict)))
                    }
                    html.push(...[
                        '   </td>',
                        '   <td>',
                        '       <a class="text-decoration-none" href="/admin/submission/' + submission.id + '">',  // ! HARDCODED
                        '           Details',
                        '       </a>',
                        '   </td>',
                        '</tr>'
                    ])
                }
                $('#submissions-' + userID + '-' + taskID).html(html.join(''))
                $('[data-bs-toggle="tooltip"]').tooltip()
                $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
                    $(this).tooltip('hide')
                })
            })
    })
}
catch (e) {}

function spinner(el) {
    $(el).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>')
}

function removeTestcase(number) {
    let numTestcases = $('#testcases').children('.testcase').length
    $('#testcase' + number).remove()
    for (let i = number; i <= numTestcases; i++) {
        $('#testcase' + i).attr('id', 'testcase' + (i-1))
        $('#testcase-number' + i).html('#' + (i-1))
        $('#testcase-number' + i).attr('id', 'testcase-number' + (i-1))
        $('#remove-testcase' + i).attr('onclick', 'removeTestcase(' + (i-1) + ')')
        $('#remove-testcase' + i).attr('id', 'remove-testcase' + (i-1))
        $('#input-label' + i).attr('for', 'input' + (i-1))
        $('#input-label' + i).attr('id', 'input-label' + (i-1))
        $('#input' + i).attr('name', 'input' + (i-1))
        $('#input' + i).attr('id', 'input' + (i-1))
        $('#answer-label' + i).attr('for', 'answer' + (i-1))
        $('#answer-label' + i).attr('id', 'answer-label' + (i-1))
        $('#answer' + i).attr('name', 'answer' + (i-1))
        $('#answer' + i).attr('id', 'answer' + (i-1))
        $('#ordered-label' + i).attr('for', 'ordered' + (i-1))
        $('#ordered-label' + i).attr('id', 'ordered-label' + (i-1))
        $('#ordered' + i).attr('name', 'ordered' + (i-1))
        $('#ordered' + i).attr('id', 'ordered' + (i-1))
    }
}

try {
    $('#new-testcase').click(() => {
        let testcasesBox = $('#testcases')
        let number = testcasesBox.children('.testcase').length + 1
        let html = [
            '<div class="testcase" id="testcase' + number + '">',
                '<div class="d-flex justify-content-between align-items-center">',
                    '<label class="form-label my-0" id="testcase-number' + number + '">#' + number + '</label>',
                    '<a class="btn btn-danger remove-testcase" id="remove-testcase' + number + '" onclick="removeTestcase(' + number + ')">Remove testcase</a>',
                '</div>',
                '<div class="row">',
                    '<div class="col-6">',
                        '<label for="input' + number + '" class="form-label" id="input-label' + number + '">Input</label>',
                        '<textarea id="input' + number + '" class="form-control consolas" name="input' + number + '" rows="5"></textarea>',
                    '</div>',
                    '<div class="col-6">',
                        '<label for="answer' + number + '" class="form-label" id="answer-label' + number + '">Answer keywords</label>',
                        '<textarea id="answer' + number + '" class="form-control consolas" name="answer' + number + '" rows="5"></textarea>',
                        '<div class="form-text">These are the keywords that must appear in the student\'s program output for it to be marked as correct. Put each answer keyword on its own line. Case-insensitive.</div>',
                        '<div class="form-check">',
                            '<input type="checkbox" value="" id="ordered' + number + '" class="form-check-input" name="ordered' + number + '">',
                            '<label for="ordered' + number + '" class="form-check-label" id="ordered-label' + number + '">',
                                'Are these keywords ordered?',
                            '</label>',
                        '</div>',
                    '</div>',
                '</div>',
                '<hr />',
            '</div>',
        ].join('\n')
        testcasesBox.append(html)
        $('.remove-testcase').click((e) => {
            removeTestcase(e)
        })
    })
}
catch (e) {}

window.onpageshow = () => {
    // Initialise tooltips.
    $('[data-bs-toggle="tooltip"]').tooltip()
    $('[data-bs-toggle="tooltip"]').on('mouseleave', function () {
        $(this).tooltip('hide')
    })
    
    try {
        // Initialise code editor.
        let editor = ace.edit('editor')
        ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.13.1/src-noconflict/')
        editor.setTheme("ace/theme/textmate")
        editor.session.setMode("ace/mode/python")
        editor.session.setUseWrapMode(true)
        editor.setOptions({ readOnly: true, highlightActiveLine: false, highlightGutterLine: false, maxLines: Infinity })
        editor.renderer.$cursorLayer.element.style.display = "none"
    }
    catch (e) {}

    try {
        $('#description-md')[0].mdContent = $('#description').val()
    }
    catch (e) {}
}
