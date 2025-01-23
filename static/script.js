document.addEventListener("DOMContentLoaded", () => {
    console.log("Web application is ready.");
});

function stopCamera() {
    fetch('/stop', { method: 'POST' })
    .then(response => response.text())
    .then(data => alert(data));
}

function shutdownServer() {
    fetch('/shutdown', { method: 'POST' })
    .then(response => response.text())
    .then(data => alert(data));
}
