document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
  
    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
  
    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });
  
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      fileInput.files = e.dataTransfer.files;
      updateFilePreview();
    });
  
    // File input change handler
    fileInput.addEventListener('change', () => {
      updateFilePreview();
    });
  });
  
  function updateFilePreview() {
    const files = document.getElementById('fileInput').files;
    const preview = document.getElementById('filePreview');
    preview.innerHTML = '';
  
    Array.from(files).forEach(file => {
      const div = document.createElement('div');
      div.className = 'file-item';
      div.innerHTML = `
        <i class="ph ph-file ${file.type.includes('pdf') ? 'ph-file-pdf' : 'ph-file-doc'}" style="font-size: 1.5rem;"></i>
        <div>
          <p class="font-medium">${file.name}</p>
          <p class="text-sm text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
      `;
      preview.appendChild(div);
    });
  }
  
  async function uploadFiles() {
    const files = document.getElementById('fileInput').files;
    const resultsDiv = document.getElementById('results');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (files.length < 2) {
      showError('Please upload at least 2 files');
      return;
    }
  
    // Clear previous results
    resultsDiv.innerHTML = '';
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `
      <div class="loading-spinner"></div>
      Analyzing...
    `;
  
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => formData.append('files', file));
  
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData
      });
  
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
  
      const data = await response.json();
      displayResults(data);
    } catch (error) {
      showError(error.message);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = `
        Analyze Documents
        <i class="ph ph-magnifying-glass"></i>
      `;
    }
  }
  
  function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
  
    if (data.error) {
      showError(data.error);
      return;
    }
  
    const sections = [
      { key: 'financial', title: 'Financial Analysis', icon: 'ph-coins' },
      { key: 'legal', title: 'Legal Review', icon: 'ph-scale' },
      { key: 'technical', title: 'Technical Evaluation', icon: 'ph-cpu' },
      { key: 'final', title: 'Final Recommendation', icon: 'ph-trophy' }
    ];
  
    sections.forEach(section => {
      if (!data[section.key]) return;
  
      const sectionDiv = document.createElement('div');
      sectionDiv.className = 'analysis-section';
      
      sectionDiv.innerHTML = `
        <div class="section-header">
          <i class="ph ${section.icon} section-icon"></i>
          <h2>${section.title}</h2>
        </div>
        <div class="content">${formatContent(data[section.key])}</div>
      `;
  
      resultsDiv.appendChild(sectionDiv);
    });
  }
  
  function formatContent(text) {
    return text
      .replace(/\n/g, '<br>')
      .replace(/- (.*?)(<br>|$)/g, '<span class="bullet">•</span> $1<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
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