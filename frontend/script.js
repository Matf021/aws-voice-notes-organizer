"use strict";

const serverUrl = "http://127.0.0.1:8000";

async function uploadAudioFile(file) {
    const reader = new FileReader();
    const base64String = await new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result.toString().replace(/^data:(.*,)?/, ''));
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });

    const response = await fetch(`${serverUrl}/upload-audio`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            filebytes: base64String,
            userId: "user123"
        })
    });

    if (!response.ok) throw new Error("Upload failed");
    return await response.json();
}

async function checkTranscription(jobName) {
    const response = await fetch(`${serverUrl}/transcription/${jobName}`);
    if (!response.ok) throw new Error("Transcription check failed");
    const data = await response.json();
    return data;
}

async function fetchTranscriptText(transcriptUrl) {
    const response = await fetch(transcriptUrl);
    if (!response.ok) throw new Error("Failed to fetch transcript text");
    const data = await response.json();
    return data.results.transcripts[0].transcript;
}

async function analyzeText(text) {
    const response = await fetch(`${serverUrl}/analyze-text`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
    });
    if (!response.ok) throw new Error("Text analysis failed");
    return await response.json();
}

async function handleUploadAndAnalyze(file) {
    try {
        const { jobName } = await uploadAudioFile(file);
        
        let transcriptData;
        let attempts = 0;
        while (attempts < 20) {
            const check = await checkTranscription(jobName);
            if (check.status === "COMPLETED") {
                transcriptData = await fetchTranscriptText(check.transcriptUrl);
                break;
            } else if (check.status === "FAILED") {
                throw new Error("Transcription failed");
            }
            await new Promise(resolve => setTimeout(resolve, 5000));
            attempts++;
        }

        if (!transcriptData) throw new Error("Timeout waiting for transcript");

        const analysis = await analyzeText(transcriptData);
        displayNote(transcriptData, analysis);

    } catch (error) {
        console.error(error);
        alert("Error: " + error.message);
    }
}

function displayNote(text, analysis) {
    const container = document.createElement("div");
    container.className = "note-card";

    const header = document.createElement("div");
    header.className = "note-header";
    const title = document.createElement("strong");
    title.innerText = analysis.keyPhrases[0] || "Voice Note";
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.innerText = analysis.sentiment;
    header.appendChild(title);
    header.appendChild(badge);

    const body = document.createElement("p");
    body.innerText = text;

    const meta = document.createElement("div");
    meta.className = "note-meta";
    meta.innerText = new Date().toLocaleString();

    const actions = document.createElement("div");
    actions.className = "note-actions";
    ["▶", "✎", "🗑"].forEach(symbol => {
        const btn = document.createElement("button");
        btn.innerText = symbol;
        actions.appendChild(btn);
    });

    container.appendChild(header);
    container.appendChild(body);
    container.appendChild(meta);
    container.appendChild(actions);

    document.body.appendChild(container);
}
