const ws =
    new WebSocket(
        "ws://localhost:8000/ws"
    );

ws.onmessage = (event) => {

    const data =
        JSON.parse(event.data);

    document.getElementById(
        "publisher"
    ).innerText =
        data.publisher;

    document.getElementById(
        "subscriber"
    ).innerText =
        data.subscriber;
};

fetch(
    "http://localhost:8000/health"
)
.then(r => r.json())
.then(data => {

    document.getElementById(
        "health"
    ).innerText =
        data.system
        ? "🟢 Healthy"
        : "🔴 Unhealthy";
});

function resetCounter()
{
    fetch(
        "http://localhost:8000/reset",
        {
            method:"POST"
        }
    );
}