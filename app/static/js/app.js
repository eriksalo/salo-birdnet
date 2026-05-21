// App-level JS utilities

// Global audio manager — only one audio plays at a time
document.addEventListener('play', (e) => {
    if (e.target.tagName === 'AUDIO') {
        document.querySelectorAll('audio').forEach(audio => {
            if (audio !== e.target) {
                audio.pause();
                audio.currentTime = 0;
            }
        });
    }
}, true);
