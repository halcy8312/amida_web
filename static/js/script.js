function selectFormat(format) {
    document.getElementById('selected-format').value = format;
    document.getElementById('mp3-button').classList.remove('selected');
    document.getElementById('wav-button').classList.remove('selected');
    document.getElementById(format + '-button').classList.add('selected');
}

window.onload = function() {
    selectFormat('mp3');
    document.getElementById('choice').value = 'audio';
    document.getElementById('audio-format').style.display = 'flex';
}

document.getElementById('choice').addEventListener('change', function () {
    var choice = this.value;
    if (choice === 'audio') {
        document.getElementById('audio-format').style.display = 'flex';
    } else {
        document.getElementById('audio-format').style.display = 'none';
    }
});     