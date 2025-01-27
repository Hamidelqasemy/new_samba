document.addEventListener('DOMContentLoaded', () => {
    initializeDragDrop();
    document.getElementById('analyzeBtn').addEventListener('click', handleAnalysis);
});

let financialChart = null;
let technicalChart = null;

function initializeDragDrop() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    // Drag and drop handlers
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleFileDrop);

    // Click handler for drop zone
    dropZone.addEventListener('click', () => fileInput.click());

    // File input change handler
    fileInput.addEventListener('change', updateFilePreview);
}

async function handleAnalysis(event) {
    event.preventDefault();
    const files = document.getElementById('fileInput').files;

    try {
        showLoadingState(true);
        const formData = createFormData(files);
        const response = await sendAnalysisRequest(formData);
        const data = await processResponse(response);

        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        showLoadingState(false);
    }
}

function createFormData(files) {
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files', file));
    return formData;
}

async function sendAnalysisRequest(formData) {
    const response = await fetch('/analyze', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
    }

    return response;
}

async function processResponse(response) {
    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    return {
        analyses: {
            financial: data.financial,
            legal: data.legal,
            technical: data.technical,
            final: data.final
        },
        scores: data.scores || {} // Ensure scores exist
    };
}

function displayResults({ analyses, scores }) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    // Display text analyses
    createAnalysisSections(resultsDiv, analyses);

    // Display visualizations if scores exist
    if (scores && Object.keys(scores).length > 0) {
        createVisualizations(resultsDiv, scores);
    } else {
        showError('No score data available for visualization');
    }
}

function createAnalysisSections(container, analyses) {
    const sections = [
        { key: 'financial', icon: 'ph-coins', title: 'Financial Analysis' },
        { key: 'legal', icon: 'ph-scale', title: 'Legal Review' },
        { key: 'technical', icon: 'ph-cpu', title: 'Technical Evaluation' },
        { key: 'final', icon: 'ph-trophy', title: 'Final Recommendation' }
    ];

    sections.forEach(({ key, icon, title }) => {
        if (!analyses[key]) return;

        const section = document.createElement('div');
        section.className = 'analysis-section';
        section.innerHTML = `
            <div class="section-header">
                <i class="ph ${icon} section-icon"></i>
                <h2>${title}</h2>
            </div>
            <div class="content">${formatAnalysisContent(analyses[key].analysis)}</div>
        `;
        container.appendChild(section);
    });
}

function formatAnalysisContent(text) {
    if (!text) return ''; // Handle undefined/null
    return String(text)  // Ensure it's a string
        .replace(/\n/g, '<br>')
        .replace(/- (.*?)(<br>|$)/g, '<span class="bullet">•</span> $1<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function createVisualizations(container, scores) {
    const isComparison = Object.keys(scores).length > 1;

    if (isComparison) {
        // Multi-file comparison mode
        const vizHTML = `
            <div class="viz-container">
                <div class="chart-card">
                    <div class="chart-title">Financial Comparison</div>
                    <canvas id="financialChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Technical Breakdown</div>
                    <canvas id="technicalChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">Proposal Scores</div>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Proposal</th>
                            <th>Financial</th>
                            <th>Technical</th>
                            <th>Legal</th>
                            <th>Overall</th>
                        </tr>
                    </thead>
                    <tbody id="comparisonBody"></tbody>
                </table>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', vizHTML);

        // Initialize charts
        financialChart = createFinancialChart(scores);
        technicalChart = createTechnicalChart(scores);
        populateComparisonTable(scores);
    } else {
        // Single-file analysis mode
        const [filename, data] = Object.entries(scores)[0];
        const summaryHTML = `
            <div class="single-file-summary">
                <h3>Detailed Scores for ${filename}</h3>
                <div class="score-card">
                    <div class="score-item">
                        <span class="score-label">Financial Health</span>
                        ${createScoreBadge(data.financial)}
                    </div>
                    <div class="score-item">
                        <span class="score-label">Technical Quality</span>
                        ${createScoreBadge(data.technical)}
                    </div>
                    <div class="score-item">
                        <span class="score-label">Legal Compliance</span>
                        ${createScoreBadge(data.legal)}
                    </div>
                    <div class="score-item highlight">
                        <span class="score-label">Overall Score</span>
                        ${createScoreBadge(data.overall)}
                    </div>
                </div>
                <div class="technical-breakdown">
                    <h4>Technical Breakdown</h4>
                    <canvas id="technicalRadar"></canvas>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', summaryHTML);

        // Initialize radar chart
        createTechnicalRadar(data.technical_breakdown);
    }
}

function createFinancialChart(scores) {
    const proposals = Object.keys(scores);
    const ctx = document.getElementById('financialChart')?.getContext('2d');
    if (!ctx) return null;

    // Validate data
    const validData = proposals.map(p => {
        const score = scores[p].financial;
        return typeof score === 'number' ? score : 0; // Fallback to 0
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: proposals,
            datasets: [{
                label: 'Financial Score',
                data: validData,
                backgroundColor: '#3b82f655',
                borderColor: '#3b82f6',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Score (%)'
                    }
                }
            }
        }
    });
}

function createTechnicalChart(scores) {
    const proposals = Object.keys(scores);
    const ctx = document.getElementById('technicalChart')?.getContext('2d');
    if (!ctx) return null;

    // Validate data
    const datasets = proposals.map((p, i) => {
        const breakdown = scores[p].technical_breakdown || [0, 0, 0, 0, 0]; // Fallback
        return {
            label: p,
            data: breakdown.map(v => typeof v === 'number' ? v : 0), // Ensure numbers
            backgroundColor: `hsl(${i * 120}, 50%, 50%, 0.2)`,
            borderColor: `hsl(${i * 120}, 50%, 50%)`,
            pointRadius: 4
        };
    });

    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Feasibility', 'Innovation', 'Scalability', 'Security', 'Compliance'],
            datasets: datasets
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function createTechnicalRadar(breakdown) {
    const ctx = document.getElementById('technicalRadar')?.getContext('2d');
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Feasibility', 'Innovation', 'Scalability', 'Security', 'Compliance'],
            datasets: [{
                label: 'Technical Scores',
                data: breakdown.map(v => typeof v === 'number' ? v : 0), // Ensure numbers
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6',
                pointRadius: 4
            }]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function populateComparisonTable(scores) {
    const tbody = document.getElementById('comparisonBody');
    if (!tbody) return;

    tbody.innerHTML = Object.entries(scores).map(([name, scores]) => `
        <tr>
            <td>${name}</td>
            <td>${createScoreBadge(scores.financial)}</td>
            <td>${createScoreBadge(scores.technical)}</td>
            <td>${createScoreBadge(scores.legal)}</td>
            <td>${createScoreBadge(scores.overall)}</td>
        </tr>
    `).join('');
}

function createScoreBadge(value) {
    const safeValue = typeof value === 'number' ? value : 'N/A'; // Handle undefined
    return `<span class="score-badge">${safeValue}%</span>`;
}

function showLoadingState(show) {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsDiv = document.getElementById('results');

    if (show) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = `
            <div class="loading-spinner"></div>
            Analyzing...
        `;
        resultsDiv.innerHTML = '<div class="loading">Processing files...</div>';
    } else {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `
            Analyze Documents
            <i class="ph ph-magnifying-glass"></i>
        `;
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    const files = e.dataTransfer.files;
    document.getElementById('fileInput').files = files;
    updateFilePreview();
    e.currentTarget.classList.remove('dragover');
}

function updateFilePreview() {
    const files = document.getElementById('fileInput').files;
    const preview = document.getElementById('filePreview');

    preview.innerHTML = Array.from(files).map(file => `
        <div class="file-item">
            <i class="ph ${file.type.includes('pdf') ? 'ph-file-pdf' : 'ph-file-doc'}"></i>
            <div>
                <p>${file.name}</p>
                <small>${(file.size / 1024 / 1024).toFixed(2)} MB</small>
            </div>
        </div>
    `).join('');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="ph ph-warning-circle"></i>
        ${message}
    `;
    document.getElementById('results').appendChild(errorDiv);
}