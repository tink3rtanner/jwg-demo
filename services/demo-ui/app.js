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
        if (data.resourceType === 'CapabilityStatement') {
            items[0].classList.add('checked');
            if (data.instantiates && data.instantiates.length > 0) {
                items[1].classList.add('checked');
            }
            if (data.rest && data.rest[0]) {
                const hasDoc = data.rest[0].resource?.some(r => r.type === 'DocumentReference');
                const hasResources = data.rest[0].resource?.some(r => ['Condition', 'Observation'].includes(r.type));
                if (hasDoc) items[2].classList.add('checked');
                if (hasResources) items[3].classList.add('checked');
                
                // Check for Patient with identifier systems
                const patientRes = data.rest[0].resource?.find(r => r.type === 'Patient');
                if (patientRes && patientRes.extension) {
                    items[4].classList.add('checked');
                }
                
                if (data.fhirVersion === '4.0.1') {
                    items[5].classList.add('checked');
                }
            }
        }
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
            checklist.querySelectorAll('li').forEach((item, idx) => {
                if (idx < 3) item.classList.add('checked'); // First 3 are required/implemented
            });
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


let publishBundleData = null;

function loadPublishBundle() {
    const fileInput = document.getElementById('publish-file');
    if (!fileInput.files[0]) return;
    
    const file = fileInput.files[0];
    const reader = new FileReader();
    
    reader.onload = function(e) {
        try {
            publishBundleData = JSON.parse(e.target.result);
            document.getElementById('publish-bundle-preview').textContent = JSON.stringify(publishBundleData, null, 2);
        } catch (error) {
            alert('Invalid JSON file: ' + error.message);
            publishBundleData = null;
        }
    };
    
    reader.readAsText(file);
}

async function executePublishDocument() {
    if (!publishBundleData) {
        alert('Please select a JSON file containing a FHIR Bundle');
        return;
    }
    
    setStatus('publish-status', 'pending', 'Publishing...');
    const resultDiv = document.getElementById('publish-result');
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${FHIR_BASE}/fhir`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/fhir+json'
            },
            body: JSON.stringify(publishBundleData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            setStatus('publish-status', 'success', `✓ ${response.status} - Document Published`);
            document.getElementById('publish-curl').textContent = `curl -X POST ${FHIR_BASE}/fhir \\
  -H "Content-Type: application/fhir+json" \\
  -d @bundle.json`;
            document.getElementById('publish-response').textContent = JSON.stringify(data, null, 2);
            resultDiv.style.display = 'grid';
            
            // Update checklist
            const checklist = document.getElementById('publish-checklist');
            if (data.resourceType === 'Bundle') {
                checklist.querySelectorAll('li').forEach((item, idx) => {
                    if (idx < 4) item.classList.add('checked');
                });
            }
            
            // Verify document appears in queries
            setTimeout(async () => {
                if (publishBundleData.entry) {
                    const docRef = publishBundleData.entry.find(e => 
                        e.resource && e.resource.resourceType === 'DocumentReference'
                    );
                    if (docRef && docRef.resource.subject) {
                        const patientRef = docRef.resource.subject.reference;
                        const docQuery = await fetch(`${FHIR_BASE}/fhir/DocumentReference?patient=${patientRef}&status=current`);
                        if (docQuery.ok) {
                            const docData = await docQuery.json();
                            if (docData.entry && docData.entry.length > 0) {
                                checklist.querySelectorAll('li')[4].classList.add('checked');
                            }
                        }
                    }
                }
            }, 1000);
        } else {
            setStatus('publish-status', 'error', `✗ ${response.status} - ${data.detail || 'Publish failed'}`);
            document.getElementById('publish-response').textContent = JSON.stringify(data, null, 2);
            resultDiv.style.display = 'grid';
        }
    } catch (error) {
        setStatus('publish-status', 'error', `✗ ${error.message}`);
    }
}

// Initialize mermaid on load
window.addEventListener('load', () => {
    mermaid.init(undefined, '#inspect-diagram');
});
