document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="media_type"]').forEach(function(elem) {
        elem.addEventListener('change', function(event) {
            if (event.target.value === 'audio') {
                document.getElementById('audio_format_selection').style.display = 'block';
            } else {
                document.getElementById('audio_format_selection').style.display = 'none';
            }
        });
    });
});

function selectFormat(format) {
    document.getElementById('audio_format').value = format;
}
