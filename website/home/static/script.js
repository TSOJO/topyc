$('.select-all').click(function() {
    if (this.checked) {
        $(this).parent().parent().find('.group-visible-check').each(function() {
            this.checked = true
        });
    } else {
        $(this).parent().parent().find('.group-visible-check').each(function() {
            this.checked = false
        });
    }
 });