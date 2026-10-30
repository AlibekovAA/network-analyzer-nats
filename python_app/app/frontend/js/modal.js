export function initializeModal() {
    const resultsModal = document.getElementById('results');
    const closeButton = resultsModal.querySelector('.close-button');

    resultsModal.addEventListener('click', (e) => {
        if (e.target === resultsModal) {
            closeResults();
        }
    });

    closeButton.addEventListener('click', () => {
        closeResults();
    });

    resultsModal.addEventListener('close', () => {
        if (document.activeElement !== document.body) return;
        const fileInput = document.getElementById('pcapFile');
        const target = fileInput.disabled ? document.querySelector('.info-icon') : fileInput;
        target.focus();
    });
}

export function showErrorMessage(message) {
    const resultsModal = document.getElementById('results');
    const modalBody = resultsModal.querySelector('.results-modal-body');

    modalBody.innerHTML = `
        <div class="error-message" role="alert">
            <p></p>
        </div>
    `;
    modalBody.querySelector('.error-message p').textContent = message;
    if (!resultsModal.open) resultsModal.showModal();
}

export function showLoadingMessage() {
    const resultsModal = document.getElementById('results');
    const modalBody = resultsModal.querySelector('.results-modal-body');

    modalBody.innerHTML = `
        <div class="loading" role="status">
            <div class="spinner" aria-hidden="true"></div>
            <p>Loading...</p>
        </div>
    `;
    if (!resultsModal.open) resultsModal.showModal();
}

export function showSuccessMessage(result) {
    const resultsModal = document.getElementById('results');
    const modalBody = resultsModal.querySelector('.results-modal-body');

    const uniqueIPs = {
        sources: [...new Set(result.packets.map(p => p.source_ip))],
        destinations: [...new Set(result.packets.map(p => p.destination_ip))]
    };

    const summaryView = {
        summary: result.summary,
        unique_ips: {
            sources: uniqueIPs.sources,
            destinations: uniqueIPs.destinations
        }
    };

    modalBody.innerHTML = `
        <div class="view-controls">
            <label class="switch">
                <input type="checkbox" id="viewToggle" aria-labelledby="viewLabel">
                <span class="slider" aria-hidden="true"></span>
            </label>
            <label class="view-label" id="viewLabel" for="viewToggle">Detailed report</label>
        </div>
        <div class="results-content">
            <pre class="summary-view"></pre>
            <pre class="detailed-view" hidden></pre>
        </div>
    `;

    const viewToggle = modalBody.querySelector('#viewToggle');
    const summaryViewEl = modalBody.querySelector('.summary-view');
    const detailedViewEl = modalBody.querySelector('.detailed-view');
    summaryViewEl.textContent = JSON.stringify(summaryView, null, 2);
    let detailedReportReady = false;

    viewToggle.addEventListener('change', () => {
        if (viewToggle.checked && !detailedReportReady) {
            detailedViewEl.textContent = JSON.stringify(result, null, 2);
            detailedReportReady = true;
        }
        summaryViewEl.hidden = viewToggle.checked;
        detailedViewEl.hidden = !viewToggle.checked;
    });

    if (!resultsModal.open) resultsModal.showModal();
}

export function closeResults() {
    const resultsModal = document.getElementById('results');
    resultsModal.close();
}
