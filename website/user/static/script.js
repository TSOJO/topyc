$('#register-form').on('submit', () => {
    $('#register-button').prop('disabled', true)
    $('#register-button').html(
        '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Registering...'
    )
})