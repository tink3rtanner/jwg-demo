const API_BASE = 'http://localhost:8082';
const FHIR_BASE = 'http://localhost:8082';

mermaid.initialize({ startOnLoad: false, theme: 'default' });

function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
    
    // Re-render mermaid diagrams
    setTimeout(() => {
        mermaid.init(undefined, `#${tabName}-diagram`);
    }, 100);
}

function setStatus(elementId, status, message) {
    const el = document.getElementById(elementId);
    el.className = `status ${status}`;
    el.textContent = message;
}

async function executeInspect() {
    setStatus('inspect-status', 'pending', 'Executing...');
    const resultDiv = document.getElementById('inspect-result');
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/metadata`);
        const data = await response.json();
        
        setStatus('inspect-status', 'success', `✓ ${response.status}`);
        document.getElementById('inspect-curl').textContent = `curl -X GET ${API_BASE}/metadata`;
        document.getElementById('inspect-response').textContent = JSON.stringify(data, null, 2);
        resultDiv.style.display = 'grid';
        
        // Update checklist
        const checklist = document.getElementById('inspect-checklist');
        const items = checklist.querySelectorAll('li');
        items.forEach(item => {
            if (data.resourceType === 'CapabilityStatement') item.classList.add('checked');
            if (data.rest && data.rest[0]) {
                const hasDoc = data.rest[0].resource?.some(r => r.type === 'DocumentReference');
                const hasResources = data.rest[0].resource?.some(r => ['Condition', 'Observation'].includes(r.type));
                if (hasDoc) items[2].classList.add('checked');
                if (hasResources) items[3].classList.add('checked');
            }
        });
    } catch (error) {
        setStatus('inspect-status', 'error', `✗ ${error.message}`);
    }
}

async function executeFindPatient() {
    setStatus('find-patient-status', 'pending', 'Executing...');
    const resultDiv = document.getElementById('find-patient-result');
    resultDiv.style.display = 'none';
    
    const identifier = document.getElementById('patient-identifier').value;
    const system = document.getElementById('patient-system').value;
    const query = `identifier=${system}|${identifier}`;
    
    try {
        const response = await fetch(`${FHIR_BASE}/fhir/Patient?${query}`);
        const data = await response.json();
        
        setStatus('find-patient-status', 'success', `✓ ${response.status}`);
        document.getElementById('find-patient-curl').textContent = `curl -X GET "${FHIR_BASE}/fhir/Patient?${query}"`;
        document.getElementById('find-patient-response').textContent = JSON.stringify(data, null, 2);
        resultDiv.style.display = 'grid';
        
        // Store patient ID for other flows
        if (data.entry && data.entry[0] && data.entry[0].resource) {
            const patientId = data.entry[0].resource.id;
            document.getElementById('doc-patient-id').value = patientId;
            document.getElementById('resource-patient-id').value = patientId;
        }
        
        // Update checklist
        const checklist = document.getElementById('find-patient-checklist');
        if (data.resourceType === 'Bundle') {
            checklist.querySelectorAll('li').forEach(item => item.classList.add('checked'));
        }
    } catch (error) {
        setStatus('find-patient-status', 'error', `✗ ${error.message}`);
    }
}

async function executeListDocuments() {
    setStatus('documents-status', 'pending', 'Executing...');
    const resultDiv = document.getElementById('documents-result');
    resultDiv.style.display = 'none';
    
    const patientId = document.getElementById('doc-patient-id').value;
    if (!patientId) {
        alert('Please find a patient first or enter a Patient ID');
        return;
    }
    
    try {
        const response = await fetch(`${FHIR_BASE}/fhir/DocumentReference?patient=Patient/${patientId}&status=current`);
        const data = await response.json();
        
        setStatus('documents-status', 'success', `✓ ${response.status}`);
        document.getElementById('documents-curl').textContent = `curl -X GET "${FHIR_BASE}/fhir/DocumentReference?patient=Patient/${patientId}&status=current"`;
        document.getElementById('documents-response').textContent = JSON.stringify(data, null, 2);
        resultDiv.style.display = 'grid';
    } catch (error) {
        setStatus('documents-status', 'error', `✗ ${error.message}`);
    }
}

async function executeQueryResources() {
    setStatus('resources-status', 'pending', 'Executing...');
    const resultDiv = document.getElementById('resources-result');
    resultDiv.style.display = 'none';
    
    const patientId = document.getElementById('resource-patient-id').value;
    if (!patientId) {
        alert('Please find a patient first or enter a Patient ID');
        return;
    }
    
    try {
        const resourceTypes = ['Condition', 'Observation', 'AllergyIntolerance', 'MedicationStatement', 'Encounter'];
        const results = {};
        
        for (const resType of resourceTypes) {
            const response = await fetch(`${FHIR_BASE}/fhir/${resType}?patient=Patient/${patientId}`);
            if (response.ok) {
                results[resType] = await response.json();
            }
        }
        
        setStatus('resources-status', 'success', '✓ Complete');
        document.getElementById('resources-curl').textContent = resourceTypes.map(t => 
            `curl -X GET "${FHIR_BASE}/fhir/${t}?patient=Patient/${patientId}"`
        ).join('\n');
        document.getElementById('resources-response').textContent = JSON.stringify(results, null, 2);
        resultDiv.style.display = 'grid';
    } catch (error) {
        setStatus('resources-status', 'error', `✗ ${error.message}`);
    }
}

async function executeImport() {
    const fileInput = document.getElementById('import-file');
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    setStatus('import-status', 'pending', 'Uploading...');
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/admin/import`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            setStatus('import-status', 'success', `✓ ${data.message || 'Imported'}`);
        } else {
            setStatus('import-status', 'error', `✗ ${data.detail || 'Import failed'}`);
        }
    } catch (error) {
        setStatus('import-status', 'error', `✗ ${error.message}`);
    }
}

async function executeExport() {
    const patientId = document.getElementById('export-patient-id').value;
    const mode = document.getElementById('export-mode').value;
    
    if (!patientId) {
        alert('Please enter a Patient ID');
        return;
    }
    
    setStatus('export-status', 'pending', 'Exporting...');
    
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('mode', mode);
    
    try {
        const response = await fetch(`${API_BASE}/admin/export`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `export_patient_${patientId}.zip`;
            a.click();
            setStatus('export-status', 'success', '✓ Downloaded');
        } else {
            const data = await response.json();
            setStatus('export-status', 'error', `✗ ${data.detail || 'Export failed'}`);
        }
    } catch (error) {
        setStatus('export-status', 'error', `✗ ${error.message}`);
    }
}

// Initialize mermaid on load
window.addEventListener('load', () => {
    mermaid.init(undefined, '#inspect-diagram');
});
