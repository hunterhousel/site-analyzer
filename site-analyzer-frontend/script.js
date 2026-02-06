// UPDATE THIS URL after you deploy the backend to Railway
const API_URL = 'https://your-backend-url.railway.app';

let currentReportPDF = null;

document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const address = document.getElementById('addressInput').value.trim();
    
    if (!address) {
        showError('Please enter an address');
        return;
    }
    
    // Show loading, hide results and errors
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address: address })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to analyze site. Please try again.');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
});

function displayResults(data) {
    // Store PDF for download
    currentReportPDF = data.report_pdf;
    
    // Update all result fields
    document.getElementById('resultAddress').textContent = data.address;
    document.getElementById('resultCoords').textContent = 
        `Coordinates: ${data.latitude.toFixed(6)}, ${data.longitude.toFixed(6)}`;
    
    document.getElementById('elevMin').textContent = `${data.elevation_min.toFixed(1)}m`;
    document.getElementById('elevMax').textContent = `${data.elevation_max.toFixed(1)}m`;
    document.getElementById('elevAvg').textContent = `${data.elevation_avg.toFixed(1)}m`;
    document.getElementById('elevChange').textContent = 
        `${data.slope_analysis.elevation_change_meters.toFixed(1)}m`;
    
    document.getElementById('slopeClass').textContent = data.slope_analysis.slope_classification;
    document.getElementById('buildability').textContent = data.slope_analysis.buildability_assessment;
    
    document.getElementById('accessScore').textContent = data.access_score;
    
    // Show results
    document.getElementById('results').classList.remove('hidden');
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.querySelector('p').textContent = message;
    errorDiv.classList.remove('hidden');
}

// Download PDF button
document.getElementById('downloadBtn').addEventListener('click', () => {
    if (!currentReportPDF) {
        showError('No report available to download');
        return;
    }
    
    // Convert base64 to blob and download
    const byteCharacters = atob(currentReportPDF);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'application/pdf' });
    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'site-analysis-report.pdf';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
});
