$('#select-all').click(function() {
    if (this.checked) {
        $('.group-visible-check').each(function() {
            this.checked = true;                        
        });
    } else {
       $('.group-visible-check').each(function() {
            this.checked = false;                        
        });
    } 
 });