const BACKEND_HOST = `${window.location.hostname}:8000`;

const healthEl = document.getElementById("health");
const connectionEl = document.getElementById("connection");
const publisherEl = document.getElementById("publisher");
const subscriberEl = document.getElementById("subscriber");
const resetBtn = document.getElementById("reset-btn");

let lastPublisher = null;
let lastSubscriber = null;

function setPill(el, state, text) {
    el.classList.remove("unknown", "good", "bad");
    el.classList.add(state);
    el.querySelector(".label").textContent = text;
}

function bump(el, value, lastValue) {
    el.textContent = value;

    if (lastValue !== null && value !== lastValue) {
        el.classList.remove("bump");
        // Force reflow so the animation can retrigger on repeated values.
        void el.offsetWidth;
        el.classList.add("bump");
    }
}

function refreshHealth() {
    fetch(`http://${BACKEND_HOST}/health`)
        .then((r) => r.json())
        .then((data) => {
            if (data.system) {
                setPill(healthEl, "good", "🟢 System Healthy");
            } else {
                setPill(healthEl, "bad", "🔴 System Unhealthy");
            }
        })
        .catch(() => {
            setPill(healthEl, "bad", "🔴 Backend Unreachable");
        });
}

function connectWebSocket() {
    const ws = new WebSocket(`ws://${BACKEND_HOST}/ws`);

    ws.onopen = () => {
        setPill(connectionEl, "good", "Live");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        bump(publisherEl, data.publisher, lastPublisher);
        bump(subscriberEl, data.subscriber, lastSubscriber);

        lastPublisher = data.publisher;
        lastSubscriber = data.subscriber;
    };

    ws.onclose = () => {
        setPill(connectionEl, "bad", "Disconnected — retrying…");
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = () => {
        ws.close();
    };
}

function resetCounter() {
    resetBtn.disabled = true;
    resetBtn.querySelector(".btn-label").textContent = "Resetting…";

    fetch(`http://${BACKEND_HOST}/reset`, { method: "POST" })
        .catch(() => {})
        .finally(() => {
            resetBtn.disabled = false;
            resetBtn.querySelector(".btn-label").textContent = "↺ Reset Counter";
        });
}

connectWebSocket();
refreshHealth();
setInterval(refreshHealth, 3000);
