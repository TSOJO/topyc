$('.select-all').click(() => {
    if (this.checked) {
        $(this).parent().parent().find('.group-visible-check').each(() => {
            this.checked = true
        });
    } else {
        $(this).parent().parent().find('.group-visible-check').each(() => {
            this.checked = false
        });
    }
 });