// Example starter JavaScript for disabling form submissions if there are invalid fields
(() => {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
                try {
                    // for register.html
                    $('#register-button').prop('disabled', false)
                    $('#register-button').html(
                        'Register'
                    )
                }
                catch {}
            }
    
            form.classList.add('was-validated')
        }, false)
    })
})()

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

function HTMLBang(tooltipText) {
    return [
        '<span>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#702963" class="bi bi-exclamation-circle-fill" viewBox="0 0 16 16" data-bs-toggle="tooltip" data-bs-title="' + tooltipText + '">',
                '<path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>',
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
