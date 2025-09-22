// Application State
let appState = {
    currentTab: 'upload',
    uploadedFile: null,
    processedData: null,
    selectedColumns: new Set(),
    piiColumns: new Set(),
    selectedAnalysisType: null,
    selectedTemplate: 'modern_blue',
    customSettings: {
        title: '',
        companyName: '',
        logoPosition: 'top-left'
    },
    generatedSlides: [],
    currentSlide: 0,
    zoomLevel: 100,
    currentPage: 0,
    rowsPerPage: 10,
    viewMode: 'full',
    chartConfigurations: {
        dashboard: [],
        insights_charts: [],
        comparison: { xAxis: '', yAxis: '', chartType: 'scatter' },
        insights_only: { columns: [] }
    },
    availableColumns: [],
    usedColumns: new Set(),
    chartInstances: []
};

// Sample data for simulation
const sampleDatasets = {
    sales: [
        { product: 'Laptop Pro', category: 'Electronics', price: 1299, quantity: 45, revenue: 58455, date: '2024-01-15', customer_email: 'john.doe@company.com', customer_name: 'John Doe', region: 'North' },
        { product: 'Smartphone X', category: 'Electronics', price: 899, quantity: 78, revenue: 70122, date: '2024-01-16', customer_email: 'jane.smith@business.com', customer_name: 'Jane Smith', region: 'South' },
        { product: 'Tablet Air', category: 'Electronics', price: 649, quantity: 32, revenue: 20768, date: '2024-01-17', customer_email: 'bob.wilson@corp.net', customer_name: 'Bob Wilson', region: 'East' },
        { product: 'Smart Watch', category: 'Wearables', price: 399, quantity: 67, revenue: 26733, date: '2024-01-18', customer_email: 'alice.brown@enterprise.org', customer_name: 'Alice Brown', region: 'West' },
        { product: 'Wireless Earbuds', category: 'Audio', price: 199, quantity: 89, revenue: 17711, date: '2024-01-19', customer_email: 'david.clark@domain.com', customer_name: 'David Clark', region: 'North' }
    ],
    customers: [
        { name: 'John Doe', email: 'john.doe@email.com', phone: '555-0123', age: 32, city: 'New York', purchases: 5, total_spent: 2500, registration_date: '2023-06-15', status: 'Premium' },
        { name: 'Jane Smith', email: 'jane.smith@email.com', phone: '555-0456', age: 28, city: 'Los Angeles', purchases: 3, total_spent: 1800, registration_date: '2023-07-22', status: 'Regular' },
        { name: 'Bob Wilson', email: 'bob.wilson@email.com', phone: '555-0789', age: 45, city: 'Chicago', purchases: 8, total_spent: 4200, registration_date: '2023-05-10', status: 'VIP' },
        { name: 'Alice Brown', email: 'alice.brown@email.com', phone: '555-0321', age: 34, city: 'Houston', purchases: 6, total_spent: 3100, registration_date: '2023-08-05', status: 'Premium' },
        { name: 'David Clark', email: 'david.clark@email.com', phone: '555-0654', age: 29, city: 'Phoenix', purchases: 4, total_spent: 2200, registration_date: '2023-09-12', status: 'Regular' }
    ]
};

// Initialize Application
function initializeApp() {
    console.log('Initializing DataPresenter app...');
    
    // Setup all event listeners
    setupEventListeners();
    
    // Set initial tab
    showTab('upload');
    
    // Generate initial slides
    generateInitialSlides();
    
    // Update metrics
    updateDownloadMetrics();
    
    // Update upload status
    updateUploadStatus('ready', 'Ready to upload');
    
    console.log('App initialized successfully');
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Tab navigation - Fixed to prevent default and ensure proper navigation
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const tabName = this.getAttribute('data-tab');
            console.log(`Navigating to tab: ${tabName}`);
            showTab(tabName);
        });
    });
    
    // File upload handlers - Fixed to properly trigger file selection
    setupFileUploadHandlers();
    
    // Data preview controls
    setupDataPreviewControls();
    
    // Template and customization handlers
    setupCustomizationHandlers();
    
    // Preview controls
    setupPreviewControls();
    
    // Download handlers
    setupDownloadHandlers();
    
    // Form input handlers
    setupFormHandlers();
    
    console.log('Event listeners setup complete');
}

function setupFileUploadHandlers() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');

    // Fixed file input trigger
    if (selectFileBtn && fileInput) {
        selectFileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Select file button clicked');
            fileInput.click();
        });
    }

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', function(e) {
            // Only trigger if not clicking the button directly
            if (!e.target.closest('#selectFileBtn')) {
                console.log('Upload zone clicked');
                fileInput.click();
            }
        });
        
        uploadZone.addEventListener('dragover', handleDragOver);
        uploadZone.addEventListener('dragleave', handleDragLeave);
        uploadZone.addEventListener('drop', handleDrop);
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            console.log('File input changed');
            handleFileSelect(e);
        });
    }
}

function setupDataPreviewControls() {
    const elements = {
        viewToggleSwitch: document.getElementById('viewToggleSwitch'),
        columnSearch: document.getElementById('columnSearch'),
        prevPage: document.getElementById('prevPage'),
        nextPage: document.getElementById('nextPage'),
        togglePiiDetails: document.getElementById('togglePiiDetails')
    };
    
    if (elements.viewToggleSwitch) {
        elements.viewToggleSwitch.addEventListener('change', toggleDataView);
    }
    if (elements.columnSearch) {
        elements.columnSearch.addEventListener('input', searchColumns);
    }
    if (elements.prevPage) {
        elements.prevPage.addEventListener('click', () => changePage(-1));
    }
    if (elements.nextPage) {
        elements.nextPage.addEventListener('click', () => changePage(1));
    }
    if (elements.togglePiiDetails) {
        elements.togglePiiDetails.addEventListener('click', togglePiiDetails);
    }
}

function setupCustomizationHandlers() {
    // Template type toggles
    document.querySelectorAll('[data-template-type]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const type = e.target.getAttribute('data-template-type');
            toggleTemplateType(type);
        });
    });

    // Template selection
    document.querySelectorAll('[data-template]').forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            const templateId = e.currentTarget.getAttribute('data-template');
            selectTemplate(templateId);
        });
    });

    // Advanced options toggle
    const toggleAdvancedBtn = document.getElementById('toggleAdvanced');
    if (toggleAdvancedBtn) {
        toggleAdvancedBtn.addEventListener('click', toggleAdvancedOptions);
    }

    // Analysis type selection
    document.querySelectorAll('[data-analysis]').forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            const analysisType = e.currentTarget.getAttribute('data-analysis');
            selectAnalysisType(analysisType);
        });
    });

    // LLM prompts
    document.querySelectorAll('.prompt-tag').forEach(tag => {
        tag.addEventListener('click', (e) => {
            const prompt = e.target.getAttribute('data-prompt');
            const llmQuery = document.getElementById('llmQuery');
            if (llmQuery && prompt) {
                llmQuery.value = prompt;
            }
        });
    });

    const generateInsightsBtn = document.getElementById('generateInsights');
    if (generateInsightsBtn) {
        generateInsightsBtn.addEventListener('click', generateInsights);
    }

    // Custom template upload
    const selectTemplateBtn = document.getElementById('selectTemplateBtn');
    const customTemplateInput = document.getElementById('customTemplateInput');
    if (selectTemplateBtn && customTemplateInput) {
        selectTemplateBtn.addEventListener('click', () => customTemplateInput.click());
        customTemplateInput.addEventListener('change', handleCustomTemplateUpload);
    }
}

function setupPreviewControls() {
    const elements = {
        zoomIn: document.getElementById('zoomIn'),
        zoomOut: document.getElementById('zoomOut'),
        fullscreen: document.getElementById('fullscreen')
    };
    
    if (elements.zoomIn) {
        elements.zoomIn.addEventListener('click', () => adjustZoom(10));
    }
    if (elements.zoomOut) {
        elements.zoomOut.addEventListener('click', () => adjustZoom(-10));
    }
    if (elements.fullscreen) {
        elements.fullscreen.addEventListener('click', toggleFullscreen);
    }
}

function setupDownloadHandlers() {
    const downloadPPTXBtn = document.getElementById('downloadPPTX');
    const downloadPDFBtn = document.getElementById('downloadPDF');
    const clearHistoryBtn = document.getElementById('clearHistory');
    
    if (downloadPPTXBtn) {
        downloadPPTXBtn.addEventListener('click', function(e) {
            e.preventDefault();
            downloadPresentation();
        });
    }
    if (downloadPDFBtn) {
        downloadPDFBtn.addEventListener('click', function(e) {
            e.preventDefault();
            downloadAsPDF();
        });
    }
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearExportHistory();
        });
    }
}

function setupFormHandlers() {
    const elements = {
        presentationTitle: document.getElementById('presentationTitle'),
        companyName: document.getElementById('companyName'),
        logoPosition: document.getElementById('logoPosition'),
        logoUpload: document.getElementById('logoUpload')
    };
    
    if (elements.presentationTitle) {
        elements.presentationTitle.addEventListener('input', (e) => {
            appState.customSettings.title = e.target.value;
        });
    }
    
    if (elements.companyName) {
        elements.companyName.addEventListener('input', (e) => {
            appState.customSettings.companyName = e.target.value;
        });
    }

    if (elements.logoPosition) {
        elements.logoPosition.addEventListener('change', (e) => {
            appState.customSettings.logoPosition = e.target.value;
        });
    }

    if (elements.logoUpload) {
        elements.logoUpload.addEventListener('change', handleLogoUpload);
    }
}

// Tab Management - Fixed to properly show/hide content
function showTab(tabName) {
    console.log(`Showing tab: ${tabName}`);
    
    // Update navigation state
    document.querySelectorAll('.nav-tab').forEach(tab => {
        const tabDataName = tab.getAttribute('data-tab');
        if (tabDataName === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Update content visibility - Fixed the logic
    document.querySelectorAll('.tab-content').forEach(content => {
        const contentId = content.id;
        const expectedId = `${tabName}-tab`;
        if (contentId === expectedId) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
    
    // Update app state
    appState.currentTab = tabName;
    
    // Trigger tab-specific initialization
    switch (tabName) {
        case 'customize':
            if (appState.processedData && appState.selectedColumns.size > 0) {
                updateAnalysisConfig();
            }
            break;
        case 'preview':
            updatePreview();
            break;
        case 'download':
            updateDownloadMetrics();
            break;
    }
}

// File Upload Handling - Fixed to actually work
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        console.log('File dropped:', files[0].name);
        processFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        console.log('File selected:', file.name);
        processFile(file);
    }
}

function processFile(file) {
    console.log('Processing file:', file.name);
    
    // For demo purposes, we'll simulate file processing without actual validation
    // In a real app, you'd validate file type and size here
    
    appState.uploadedFile = file;
    
    // Show upload progress
    showUploadProgress();
    updateUploadStatus('uploading', 'Processing file...');
    
    // Simulate file processing
    setTimeout(() => {
        simulateDataProcessing(file);
    }, 1500);
}

function showUploadProgress() {
    const uploadZone = document.getElementById('uploadZone');
    const progressDiv = uploadZone.querySelector('.upload-progress');
    const progressFill = document.getElementById('progressFill');
    
    if (progressDiv) progressDiv.classList.remove('hidden');
    
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress >= 100) {
            progress = 100;
            clearInterval(progressInterval);
        }
        if (progressFill) progressFill.style.width = `${progress}%`;
    }, 200);
}

function simulateDataProcessing(file) {
    console.log('Simulating data processing...');
    
    // Determine dataset type from filename
    const fileName = file.name.toLowerCase();
    let datasetType = 'sales';
    if (fileName.includes('customer') || fileName.includes('user')) {
        datasetType = 'customers';
    }
    
    // Generate larger sample dataset
    const sampleData = generateSampleData(datasetType, 150);
    
    appState.processedData = {
        fileName: file.name,
        data: sampleData,
        columns: Object.keys(sampleData[0]),
        totalRows: sampleData.length,
        totalColumns: Object.keys(sampleData[0]).length
    };

    appState.availableColumns = [...appState.processedData.columns];

    // Process and display data
    displayDataPreview();
    displayColumnSelection();
    simulatePIIDetection();
    updateDatasetMetrics();
    showCorrelationSuggestions();
    
    updateUploadStatus('success', 'File processed successfully');
    
    // Show all data sections
    const sections = ['viewToggle', 'dataPreview', 'columnSelection', 'piiDetection', 'suggestionsPanel'];
    sections.forEach(sectionId => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.classList.remove('hidden');
            element.classList.add('fade-in');
        }
    });
    
    console.log('Data processing simulation complete');
}

function generateSampleData(type, count) {
    const data = [];
    const base = sampleDatasets[type] || sampleDatasets.sales;
    
    for (let i = 0; i < count; i++) {
        const item = { ...base[i % base.length] };
        
        // Add variation to make data more realistic
        if (item.price) {
            item.price = Math.max(99, item.price + Math.floor(Math.random() * 200) - 100);
        }
        if (item.quantity) {
            item.quantity = Math.max(1, item.quantity + Math.floor(Math.random() * 40) - 20);
        }
        if (item.revenue) {
            item.revenue = item.price * item.quantity;
        }
        if (item.age) {
            item.age = Math.max(18, Math.min(80, item.age + Math.floor(Math.random() * 20) - 10));
        }
        if (item.total_spent) {
            item.total_spent = Math.max(100, item.total_spent + Math.floor(Math.random() * 1000) - 500);
        }
        
        // Add unique identifiers
        if (item.product) {
            item.product = `${item.product} ${String.fromCharCode(65 + (i % 26))}${i + 1}`;
        }
        if (item.name) {
            const names = ['John', 'Jane', 'Bob', 'Alice', 'David', 'Sarah', 'Mike', 'Lisa'];
            const surnames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'];
            item.name = `${names[i % names.length]} ${surnames[(i + 3) % surnames.length]}`;
        }
        
        data.push(item);
    }
    
    return data;
}

// Data Display Functions
function displayDataPreview() {
    const headers = document.getElementById('tableHeaders');
    const body = document.getElementById('tableBody');
    
    if (!appState.processedData || !headers || !body) return;
    
    // Create headers
    headers.innerHTML = '';
    const columnsToShow = getColumnsToShow();
    
    columnsToShow.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        th.addEventListener('click', () => sortTable(column));
        headers.appendChild(th);
    });
    
    // Update pagination and show rows
    updatePagination();
    displayTableRows();
}

function getColumnsToShow() {
    if (appState.viewMode === 'selected' && appState.selectedColumns.size > 0) {
        return Array.from(appState.selectedColumns);
    }
    return appState.processedData.columns;
}

function displayTableRows() {
    const body = document.getElementById('tableBody');
    if (!body || !appState.processedData) return;
    
    body.innerHTML = '';
    
    const startIndex = appState.currentPage * appState.rowsPerPage;
    const endIndex = startIndex + appState.rowsPerPage;
    const pageData = appState.processedData.data.slice(startIndex, endIndex);
    const columnsToShow = getColumnsToShow();
    
    pageData.forEach(row => {
        const tr = document.createElement('tr');
        columnsToShow.forEach(column => {
            const td = document.createElement('td');
            td.textContent = row[column] || '-';
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });
}

function updatePagination() {
    if (!appState.processedData) return;
    
    const totalPages = Math.ceil(appState.processedData.totalRows / appState.rowsPerPage);
    const currentPageNum = appState.currentPage + 1;
    
    const pageInfo = document.getElementById('pageInfo');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    if (pageInfo) {
        pageInfo.textContent = `Page ${currentPageNum} of ${totalPages}`;
    }
    
    if (prevBtn) {
        prevBtn.disabled = appState.currentPage === 0;
    }
    
    if (nextBtn) {
        nextBtn.disabled = appState.currentPage >= totalPages - 1;
    }
}

function changePage(direction) {
    if (!appState.processedData) return;
    
    const totalPages = Math.ceil(appState.processedData.totalRows / appState.rowsPerPage);
    const newPage = appState.currentPage + direction;
    
    if (newPage >= 0 && newPage < totalPages) {
        appState.currentPage = newPage;
        displayTableRows();
        updatePagination();
    }
}

function displayColumnSelection() {
    const grid = document.getElementById('columnsGrid');
    if (!appState.processedData || !grid) return;
    
    grid.innerHTML = '';
    
    appState.processedData.columns.forEach(column => {
        const columnData = appState.processedData.data.map(row => row[column]);
        const stats = calculateColumnStats(columnData);
        
        const card = document.createElement('div');
        card.className = 'column-card';
        card.innerHTML = `
            <div class="column-header">
                <span class="column-name">${column}</span>
                <input type="checkbox" class="column-checkbox" data-column="${column}">
            </div>
            <div class="column-meta">
                <span>Type: ${stats.type}</span>
                <span>Null: ${stats.nullPercent}%</span>
                <span>Unique: ${stats.uniquePercent}%</span>
                <span>Values: ${stats.valueCount}</span>
            </div>
            <div class="column-actions">
                <button class="btn btn--outline btn--sm mark-pii-btn" data-column="${column}">Mark as PII</button>
            </div>
        `;
        
        // Add event listeners
        const checkbox = card.querySelector('.column-checkbox');
        checkbox.addEventListener('change', (e) => {
            toggleColumnSelection(column, e.target.checked);
        });
        
        const piiBtn = card.querySelector('.mark-pii-btn');
        piiBtn.addEventListener('click', (e) => {
            e.preventDefault();
            togglePII(column);
        });
        
        grid.appendChild(card);
    });
}

function calculateColumnStats(columnData) {
    const nonNullData = columnData.filter(val => val !== null && val !== undefined && val !== '');
    const uniqueValues = new Set(nonNullData);
    
    let type = 'String';
    if (nonNullData.length > 0) {
        const firstValue = nonNullData[0];
        if (!isNaN(firstValue) && typeof firstValue === 'number') {
            type = 'Number';
        } else if (!isNaN(Date.parse(firstValue))) {
            type = 'Date';
        } else if (typeof firstValue === 'string' && firstValue.includes('@')) {
            type = 'Email';
        }
    }
    
    return {
        type,
        nullPercent: Math.round(((columnData.length - nonNullData.length) / columnData.length) * 100),
        uniquePercent: Math.round((uniqueValues.size / nonNullData.length) * 100),
        valueCount: nonNullData.length
    };
}

function toggleColumnSelection(column, selected) {
    if (selected) {
        appState.selectedColumns.add(column);
    } else {
        appState.selectedColumns.delete(column);
        // Also remove from used columns and chart configurations
        appState.usedColumns.delete(column);
        removeColumnFromConfigurations(column);
    }
    
    // Update card appearance
    const card = document.querySelector(`[data-column="${column}"]`)?.closest('.column-card');
    if (card) {
        card.classList.toggle('selected', selected);
    }
    
    // Update data preview if in selected mode
    if (appState.viewMode === 'selected') {
        displayDataPreview();
    }
    
    // Update analysis configuration if active
    if (appState.selectedAnalysisType) {
        updateAnalysisConfig();
        updateChartPreviews();
    }
    
    console.log(`Column ${column} ${selected ? 'selected' : 'deselected'}. Total selected: ${appState.selectedColumns.size}`);
}

function removeColumnFromConfigurations(column) {
    // Remove from dashboard configurations
    appState.chartConfigurations.dashboard = appState.chartConfigurations.dashboard.filter(config => config.column !== column);
    
    // Remove from insights configurations
    appState.chartConfigurations.insights_charts = appState.chartConfigurations.insights_charts.filter(config => config.column !== column);
    
    // Remove from comparison if used
    if (appState.chartConfigurations.comparison.xAxis === column) {
        appState.chartConfigurations.comparison.xAxis = '';
    }
    if (appState.chartConfigurations.comparison.yAxis === column) {
        appState.chartConfigurations.comparison.yAxis = '';
    }
    
    // Remove from insights only
    appState.chartConfigurations.insights_only.columns = appState.chartConfigurations.insights_only.columns.filter(col => col !== column);
}

function simulatePIIDetection() {
    if (!appState.processedData) return;
    
    // Simulate PII detection with more sophisticated patterns
    const piiPatterns = {
        email: /email|mail/i,
        name: /name|firstname|lastname|customer_name/i,
        phone: /phone|mobile|tel/i,
        address: /address|street|city|zip/i,
        ssn: /ssn|social/i
    };
    
    appState.piiColumns.clear();
    
    appState.processedData.columns.forEach(column => {
        Object.keys(piiPatterns).forEach(pattern => {
            if (piiPatterns[pattern].test(column)) {
                appState.piiColumns.add(column);
            }
        });
    });
    
    updatePIIDisplay();
}

function updatePIIDisplay() {
    const count = document.getElementById('piiCount');
    const details = document.getElementById('piiDetails');
    
    if (count) {
        count.textContent = `${appState.piiColumns.size} PII columns detected`;
    }
    
    if (details) {
        details.innerHTML = '';
        appState.piiColumns.forEach(column => {
            const div = document.createElement('div');
            div.className = 'pii-item';
            div.innerHTML = `
                <div class="pii-info">
                    <div class="pii-column">${column}</div>
                    <div class="pii-reason">Contains personally identifiable information</div>
                </div>
                <div class="pii-actions">
                    <button class="btn btn--outline btn--sm" onclick="removePII('${column}')">Remove from PII</button>
                    <button class="btn btn--primary btn--sm" onclick="addToAnalysis('${column}')">Add to Analysis</button>
                </div>
            `;
            details.appendChild(div);
        });
    }
}

function togglePII(column) {
    if (appState.piiColumns.has(column)) {
        appState.piiColumns.delete(column);
    } else {
        appState.piiColumns.add(column);
    }
    updatePIIDisplay();
}

function removePII(column) {
    appState.piiColumns.delete(column);
    updatePIIDisplay();
}

function addToAnalysis(column) {
    appState.selectedColumns.add(column);
    appState.piiColumns.delete(column);
    
    // Update checkbox
    const checkbox = document.querySelector(`[data-column="${column}"]`);
    if (checkbox) {
        checkbox.checked = true;
        toggleColumnSelection(column, true);
    }
    
    updatePIIDisplay();
}

function updateDatasetMetrics() {
    if (!appState.processedData) return;
    
    const nullCount = appState.processedData.data.reduce((count, row) => {
        return count + Object.values(row).filter(val => val === null || val === undefined || val === '').length;
    }, 0);
    
    const totalCells = appState.processedData.totalRows * appState.processedData.totalColumns;
    const completeness = Math.round(((totalCells - nullCount) / totalCells) * 100);
    
    const elements = {
        rowCount: document.getElementById('rowCount'),
        columnCount: document.getElementById('columnCount'),
        nullValues: document.getElementById('nullValues'),
        completeness: document.getElementById('completeness'),
        completenessCard: document.getElementById('completenessCard')
    };
    
    if (elements.rowCount) elements.rowCount.textContent = appState.processedData.totalRows.toLocaleString();
    if (elements.columnCount) elements.columnCount.textContent = appState.processedData.totalColumns;
    if (elements.nullValues) elements.nullValues.textContent = nullCount.toLocaleString();
    
    if (elements.completeness) {
        elements.completeness.textContent = `${completeness}%`;
        
        // Update card styling based on completeness
        if (elements.completenessCard) {
            elements.completenessCard.className = 'metric-card';
            if (completeness >= 90) {
                elements.completenessCard.classList.add('quality-good');
            } else if (completeness >= 70) {
                elements.completenessCard.classList.add('quality-warning');
            } else {
                elements.completenessCard.classList.add('quality-error');
            }
        }
    }
    
    console.log(`Dataset metrics updated: ${appState.processedData.totalRows} rows, ${appState.processedData.totalColumns} columns, ${completeness}% complete`);
}

function showCorrelationSuggestions() {
    if (!appState.processedData) return;
    
    const numericColumns = appState.processedData.columns.filter(column => {
        const columnData = appState.processedData.data.map(row => row[column]);
        return columnData.some(val => !isNaN(val) && typeof val === 'number');
    });
    
    const suggestions = numericColumns.slice(0, 6).map(column => ({
        name: column,
        score: (Math.random() * 0.8 + 0.2).toFixed(2)
    }));
    
    const list = document.getElementById('suggestionsList');
    if (list) {
        list.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerHTML = `
                <div class="suggestion-info">
                    <div class="suggestion-name">${suggestion.name}</div>
                    <div class="suggestion-score">${(suggestion.score * 100).toFixed(0)}% correlation</div>
                </div>
                <button class="btn btn--outline btn--sm" onclick="addSuggestionToAnalysis('${suggestion.name}')">Add</button>
            `;
            list.appendChild(div);
        });
    }
}

function addSuggestionToAnalysis(column) {
    appState.selectedColumns.add(column);
    const checkbox = document.querySelector(`[data-column="${column}"]`);
    if (checkbox) {
        checkbox.checked = true;
        toggleColumnSelection(column, true);
    }
}

// Analysis Type Management
function selectAnalysisType(type) {
    // Update active state
    document.querySelectorAll('.analysis-card').forEach(card => {
        card.classList.remove('active');
    });
    
    const selectedCard = document.querySelector(`[data-analysis="${type}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }
    
    appState.selectedAnalysisType = type;
    appState.usedColumns.clear();
    
    console.log(`Analysis type selected: ${type}`);
    
    updateAnalysisConfig();
    updateChartPreviews();
}

function updateAnalysisConfig() {
    const content = document.getElementById('configContent');
    if (!content) return;
    
    if (!appState.selectedAnalysisType) {
        content.innerHTML = '<p class="config-placeholder">Select an analysis type above to configure charts and settings.</p>';
        return;
    }
    
    if (!appState.processedData || appState.selectedColumns.size === 0) {
        content.innerHTML = '<p class="config-placeholder">Please upload data and select columns first.</p>';
        return;
    }
    
    const availableColumns = Array.from(appState.selectedColumns);
    let configHTML = '';
    
    switch (appState.selectedAnalysisType) {
        case 'dashboard':
            configHTML = generateDashboardConfig(availableColumns);
            break;
        case 'insights_charts':
            configHTML = generateInsightsChartsConfig(availableColumns);
            break;
        case 'insights_only':
            configHTML = generateInsightsOnlyConfig(availableColumns);
            break;
        case 'comparison':
            configHTML = generateComparisonConfig(availableColumns);
            break;
    }
    
    content.innerHTML = configHTML;
    setupConfigEventListeners();
}

function generateDashboardConfig(availableColumns) {
    const currentConfigs = appState.chartConfigurations.dashboard || [];
    let html = `
        <div class="analysis-config-section">
            <h4>Dashboard Configuration (Max 6 Charts)</h4>
            <p>Each chart must use a unique column from your selected data.</p>
            <div class="chart-config" id="dashboardCharts">
    `;
    
    // Show existing configurations
    for (let i = 0; i < Math.max(1, currentConfigs.length); i++) {
        const config = currentConfigs[i] || { column: '', chartType: 'bar' };
        const usedColumns = currentConfigs.map(c => c.column).filter(c => c && c !== config.column);
        const availableForThis = availableColumns.filter(col => !usedColumns.includes(col));
        
        html += `
            <div class="chart-item" data-chart-index="${i}">
                <h5>Chart ${i + 1}</h5>
                <div class="form-group">
                    <label class="form-label">Column</label>
                    <select class="form-control chart-column-select" data-type="dashboard" data-index="${i}">
                        <option value="">Select column...</option>
                        ${availableForThis.map(col => 
                            `<option value="${col}" ${config.column === col ? 'selected' : ''}>${col}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Chart Type</label>
                    <select class="form-control chart-type-select" data-type="dashboard" data-index="${i}">
                        <option value="bar" ${config.chartType === 'bar' ? 'selected' : ''}>Bar Chart</option>
                        <option value="line" ${config.chartType === 'line' ? 'selected' : ''}>Line Chart</option>
                        <option value="pie" ${config.chartType === 'pie' ? 'selected' : ''}>Pie Chart</option>
                        <option value="scatter" ${config.chartType === 'scatter' ? 'selected' : ''}>Scatter Plot</option>
                        <option value="area" ${config.chartType === 'area' ? 'selected' : ''}>Area Chart</option>
                        <option value="histogram" ${config.chartType === 'histogram' ? 'selected' : ''}>Histogram</option>
                    </select>
                </div>
                ${i > 0 ? `<button class="btn btn--outline btn--sm remove-chart" data-index="${i}">Remove</button>` : ''}
            </div>
        `;
    }
    
    html += `</div>`;
    
    if (currentConfigs.length < 6) {
        html += `<button class="btn btn--outline add-chart-btn" data-type="dashboard">Add Chart (${currentConfigs.length}/6)</button>`;
    }
    
    html += `</div>`;
    return html;
}

function generateInsightsChartsConfig(availableColumns) {
    const currentConfigs = appState.chartConfigurations.insights_charts || [];
    let html = `
        <div class="analysis-config-section">
            <h4>Insights + Charts Configuration</h4>
            <p>Each insight analyzes one column with a corresponding chart.</p>
            <div class="chart-config" id="insightsCharts">
    `;
    
    for (let i = 0; i < Math.max(1, currentConfigs.length); i++) {
        const config = currentConfigs[i] || { column: '', chartType: 'bar' };
        const usedColumns = currentConfigs.map(c => c.column).filter(c => c && c !== config.column);
        const availableForThis = availableColumns.filter(col => !usedColumns.includes(col));
        
        html += `
            <div class="chart-item" data-chart-index="${i}">
                <h5>Insight ${i + 1}</h5>
                <div class="form-group">
                    <label class="form-label">Column</label>
                    <select class="form-control chart-column-select" data-type="insights_charts" data-index="${i}">
                        <option value="">Select column...</option>
                        ${availableForThis.map(col => 
                            `<option value="${col}" ${config.column === col ? 'selected' : ''}>${col}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Chart Type</label>
                    <select class="form-control chart-type-select" data-type="insights_charts" data-index="${i}">
                        <option value="bar" ${config.chartType === 'bar' ? 'selected' : ''}>Bar Chart</option>
                        <option value="line" ${config.chartType === 'line' ? 'selected' : ''}>Line Chart</option>
                        <option value="pie" ${config.chartType === 'pie' ? 'selected' : ''}>Pie Chart</option>
                        <option value="scatter" ${config.chartType === 'scatter' ? 'selected' : ''}>Scatter Plot</option>
                        <option value="area" ${config.chartType === 'area' ? 'selected' : ''}>Area Chart</option>
                    </select>
                </div>
                ${i > 0 ? `<button class="btn btn--outline btn--sm remove-chart" data-index="${i}">Remove</button>` : ''}
            </div>
        `;
    }
    
    html += `</div>`;
    html += `<button class="btn btn--outline add-chart-btn" data-type="insights_charts">Add Insight</button>`;
    html += `</div>`;
    return html;
}

function generateInsightsOnlyConfig(availableColumns) {
    const selectedColumns = appState.chartConfigurations.insights_only.columns || [];
    
    let html = `
        <div class="analysis-config-section">
            <h4>Text Analysis Configuration</h4>
            <p>Select columns for comprehensive text-based analysis.</p>
            <div class="form-group">
                <label class="form-label">Columns for Analysis</label>
                <div class="column-checkboxes" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
    `;
    
    availableColumns.forEach(column => {
        const isSelected = selectedColumns.includes(column);
        html += `
            <label class="column-checkbox-label" style="display: flex; align-items: center; gap: 8px; padding: 8px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); cursor: pointer;">
                <input type="checkbox" class="insights-column-checkbox" 
                       value="${column}" ${isSelected ? 'checked' : ''}>
                <span>${column}</span>
            </label>
        `;
    });
    
    html += `
                </div>
            </div>
        </div>
    `;
    
    return html;
}

function generateComparisonConfig(availableColumns) {
    const config = appState.chartConfigurations.comparison;
    const availableForY = availableColumns.filter(col => col !== config.xAxis);
    const availableForX = availableColumns.filter(col => col !== config.yAxis);
    
    return `
        <div class="analysis-config-section">
            <h4>Comparison Configuration</h4>
            <p>Compare two columns against each other.</p>
            <div class="options-grid">
                <div class="form-group">
                    <label class="form-label">X-Axis Column</label>
                    <select class="form-control" id="comparisonXAxis">
                        <option value="">Select column...</option>
                        ${availableForX.map(col => 
                            `<option value="${col}" ${config.xAxis === col ? 'selected' : ''}>${col}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Y-Axis Column</label>
                    <select class="form-control" id="comparisonYAxis">
                        <option value="">Select column...</option>
                        ${availableForY.map(col => 
                            `<option value="${col}" ${config.yAxis === col ? 'selected' : ''}>${col}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Chart Type</label>
                    <select class="form-control" id="comparisonChartType">
                        <option value="scatter" ${config.chartType === 'scatter' ? 'selected' : ''}>Scatter Plot</option>
                        <option value="line" ${config.chartType === 'line' ? 'selected' : ''}>Line Chart</option>
                        <option value="bar" ${config.chartType === 'bar' ? 'selected' : ''}>Bar Chart</option>
                    </select>
                </div>
            </div>
        </div>
    `;
}

function setupConfigEventListeners() {
    // Chart column and type selectors
    document.querySelectorAll('.chart-column-select, .chart-type-select').forEach(select => {
        select.addEventListener('change', handleChartConfigChange);
    });
    
    // Add/Remove chart buttons
    document.querySelectorAll('.add-chart-btn').forEach(btn => {
        btn.addEventListener('click', handleAddChart);
    });
    
    document.querySelectorAll('.remove-chart').forEach(btn => {
        btn.addEventListener('click', handleRemoveChart);
    });
    
    // Comparison selectors
    const comparisonSelectors = ['comparisonXAxis', 'comparisonYAxis', 'comparisonChartType'];
    comparisonSelectors.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', handleComparisonChange);
        }
    });
    
    // Insights only checkboxes
    document.querySelectorAll('.insights-column-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleInsightsOnlyChange);
    });
}

function handleChartConfigChange(e) {
    const type = e.target.dataset.type;
    const index = parseInt(e.target.dataset.index);
    const isColumn = e.target.classList.contains('chart-column-select');
    const isChartType = e.target.classList.contains('chart-type-select');
    
    if (!appState.chartConfigurations[type]) {
        appState.chartConfigurations[type] = [];
    }
    
    // Ensure the configuration object exists
    if (!appState.chartConfigurations[type][index]) {
        appState.chartConfigurations[type][index] = { column: '', chartType: 'bar' };
    }
    
    if (isColumn) {
        const oldColumn = appState.chartConfigurations[type][index].column;
        const newColumn = e.target.value;
        
        // Update used columns
        if (oldColumn) appState.usedColumns.delete(oldColumn);
        if (newColumn) appState.usedColumns.add(newColumn);
        
        appState.chartConfigurations[type][index].column = newColumn;
        
        console.log(`Chart ${index + 1} column changed to: ${newColumn}`);
        
        // Refresh the config to update available columns for other selects
        updateAnalysisConfig();
    }
    
    if (isChartType) {
        appState.chartConfigurations[type][index].chartType = e.target.value;
        console.log(`Chart ${index + 1} type changed to: ${e.target.value}`);
    }
    
    updateChartPreviews();
}

function handleAddChart(e) {
    const type = e.target.dataset.type;
    
    if (!appState.chartConfigurations[type]) {
        appState.chartConfigurations[type] = [];
    }
    
    // Add new empty configuration
    appState.chartConfigurations[type].push({ column: '', chartType: 'bar' });
    
    console.log(`Added new chart to ${type}. Total: ${appState.chartConfigurations[type].length}`);
    
    updateAnalysisConfig();
}

function handleRemoveChart(e) {
    const index = parseInt(e.target.dataset.index);
    const type = appState.selectedAnalysisType;
    
    if (appState.chartConfigurations[type] && appState.chartConfigurations[type][index]) {
        const removedConfig = appState.chartConfigurations[type][index];
        if (removedConfig.column) {
            appState.usedColumns.delete(removedConfig.column);
        }
        
        appState.chartConfigurations[type].splice(index, 1);
        
        console.log(`Removed chart ${index + 1} from ${type}`);
    }
    
    updateAnalysisConfig();
    updateChartPreviews();
}

function handleComparisonChange(e) {
    const field = e.target.id.replace('comparison', '').toLowerCase();
    const fieldMap = {
        'xaxis': 'xAxis',
        'yaxis': 'yAxis',
        'charttype': 'chartType'
    };
    
    const actualField = fieldMap[field] || field;
    appState.chartConfigurations.comparison[actualField] = e.target.value;
    
    console.log(`Comparison ${actualField} changed to: ${e.target.value}`);
    
    // Update available columns for the other axis
    if (actualField === 'xAxis' || actualField === 'yAxis') {
        updateAnalysisConfig();
    }
    
    updateChartPreviews();
}

function handleInsightsOnlyChange(e) {
    const column = e.target.value;
    const isChecked = e.target.checked;
    
    if (!appState.chartConfigurations.insights_only.columns) {
        appState.chartConfigurations.insights_only.columns = [];
    }
    
    if (isChecked) {
        if (!appState.chartConfigurations.insights_only.columns.includes(column)) {
            appState.chartConfigurations.insights_only.columns.push(column);
        }
    } else {
        appState.chartConfigurations.insights_only.columns = 
            appState.chartConfigurations.insights_only.columns.filter(col => col !== column);
    }
    
    console.log(`Insights Only columns: ${appState.chartConfigurations.insights_only.columns.join(', ')}`);
    
    updateChartPreviews();
}

// Chart Preview Functions
function updateChartPreviews() {
    const container = document.getElementById('chartPreviewContainer');
    if (!container) return;
    
    // Clear existing chart instances
    appState.chartInstances.forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    appState.chartInstances = [];
    
    if (!appState.selectedAnalysisType || !appState.processedData) {
        container.innerHTML = `
            <div class="preview-placeholder">
                <div class="preview-placeholder-icon">📊</div>
                <p>Chart previews will appear here after configuration</p>
            </div>
        `;
        return;
    }
    
    const configs = appState.chartConfigurations[appState.selectedAnalysisType];
    
    switch (appState.selectedAnalysisType) {
        case 'dashboard':
            generateDashboardPreviews(container, configs);
            break;
        case 'insights_charts':
            generateInsightsPreviews(container, configs);
            break;
        case 'insights_only':
            generateInsightsOnlyPreview(container, configs);
            break;
        case 'comparison':
            generateComparisonPreview(container, configs);
            break;
    }
    
    console.log(`Chart previews updated for ${appState.selectedAnalysisType}`);
}

function generateDashboardPreviews(container, configs) {
    const validConfigs = configs.filter(config => config && config.column);
    
    if (validConfigs.length === 0) {
        container.innerHTML = `
            <div class="preview-placeholder">
                <div class="preview-placeholder-icon">📊</div>
                <p>Configure charts above to see previews</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `<div class="chart-previews-grid" id="chartPreviewsGrid"></div>`;
    const grid = document.getElementById('chartPreviewsGrid');
    
    validConfigs.forEach((config, index) => {
        const chartItem = document.createElement('div');
        chartItem.className = 'chart-preview-item';
        chartItem.innerHTML = `
            <h6>${config.column} - ${config.chartType.charAt(0).toUpperCase() + config.chartType.slice(1)} Chart</h6>
            <div class="chart-canvas-container" style="position: relative; height: 180px;">
                <canvas id="chart-${index}"></canvas>
            </div>
        `;
        grid.appendChild(chartItem);
        
        // Generate chart
        setTimeout(() => {
            const chart = generateChart(`chart-${index}`, config.column, config.chartType);
            if (chart) {
                appState.chartInstances.push(chart);
            }
        }, 100);
    });
}

function generateInsightsPreviews(container, configs) {
    const validConfigs = configs.filter(config => config && config.column);
    
    if (validConfigs.length === 0) {
        container.innerHTML = `
            <div class="preview-placeholder">
                <div class="preview-placeholder-icon">📈</div>
                <p>Configure insights above to see previews</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `<div class="chart-previews-grid" id="chartPreviewsGrid"></div>`;
    const grid = document.getElementById('chartPreviewsGrid');
    
    validConfigs.forEach((config, index) => {
        const chartItem = document.createElement('div');
        chartItem.className = 'chart-preview-item';
        chartItem.innerHTML = `
            <h6>Insight ${index + 1}: ${config.column} Analysis</h6>
            <div class="chart-canvas-container" style="position: relative; height: 180px;">
                <canvas id="insight-chart-${index}"></canvas>
            </div>
        `;
        grid.appendChild(chartItem);
        
        // Generate chart
        setTimeout(() => {
            const chart = generateChart(`insight-chart-${index}`, config.column, config.chartType);
            if (chart) {
                appState.chartInstances.push(chart);
            }
        }, 100);
    });
}

function generateInsightsOnlyPreview(container, configs) {
    const selectedColumns = configs.columns || [];
    
    if (selectedColumns.length === 0) {
        container.innerHTML = `
            <div class="preview-placeholder">
                <div class="preview-placeholder-icon">📝</div>
                <p>Select columns above for text analysis</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="insights-text-preview" style="padding: 20px; background: var(--color-bg-1); border-radius: var(--radius-base);">
            <h6>Text Analysis Preview</h6>
            <div class="text-analysis-content">
                <p><strong>Selected Columns:</strong> ${selectedColumns.join(', ')}</p>
                <p><strong>Analysis Type:</strong> Comprehensive text-based insights</p>
                <p><strong>Output:</strong> Statistical summaries, patterns, and business recommendations</p>
                <div class="sample-insight" style="margin-top: 15px; padding: 15px; background: var(--color-surface); border-radius: var(--radius-sm);">
                    <h6>Sample Insight:</h6>
                    <p>Analysis of ${selectedColumns[0]} reveals significant patterns that can inform strategic decision-making...</p>
                </div>
            </div>
        </div>
    `;
}

function generateComparisonPreview(container, config) {
    if (!config.xAxis || !config.yAxis) {
        container.innerHTML = `
            <div class="preview-placeholder">
                <div class="preview-placeholder-icon">⚖️</div>
                <p>Select X and Y axis columns to see comparison preview</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="chart-preview-item">
            <h6>${config.xAxis} vs ${config.yAxis} - ${config.chartType.charAt(0).toUpperCase() + config.chartType.slice(1)} Chart</h6>
            <div class="chart-canvas-container" style="position: relative; height: 240px;">
                <canvas id="comparison-chart"></canvas>
            </div>
        </div>
    `;
    
    // Generate comparison chart
    setTimeout(() => {
        const chart = generateComparisonChart('comparison-chart', config.xAxis, config.yAxis, config.chartType);
        if (chart) {
            appState.chartInstances.push(chart);
        }
    }, 100);
}

function generateChart(canvasId, column, chartType) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !appState.processedData) return null;
    
    const ctx = canvas.getContext('2d');
    const columnData = appState.processedData.data.map(row => row[column]);
    
    // Process data based on column type
    const processedData = processColumnDataForChart(columnData, chartType);
    
    const config = {
        type: chartType === 'histogram' ? 'bar' : chartType,
        data: processedData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: chartType === 'pie',
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: column
                }
            },
            scales: chartType !== 'pie' ? {
                y: {
                    beginAtZero: true
                }
            } : {}
        }
    };
    
    try {
        return new Chart(ctx, config);
    } catch (error) {
        console.error('Error creating chart:', error);
        return null;
    }
}

function generateComparisonChart(canvasId, xColumn, yColumn, chartType) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !appState.processedData) return null;
    
    const ctx = canvas.getContext('2d');
    const data = appState.processedData.data.slice(0, 20).map(row => ({
        x: row[xColumn],
        y: row[yColumn]
    }));
    
    const config = {
        type: chartType,
        data: {
            datasets: [{
                label: `${xColumn} vs ${yColumn}`,
                data: data,
                backgroundColor: '#1FB8CD',
                borderColor: '#1FB8CD',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${xColumn} vs ${yColumn}`
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xColumn
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: yColumn
                    }
                }
            }
        }
    };
    
    try {
        return new Chart(ctx, config);
    } catch (error) {
        console.error('Error creating comparison chart:', error);
        return null;
    }
}

function processColumnDataForChart(columnData, chartType) {
    const colors = ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325', '#944454', '#13343B'];
    
    if (chartType === 'pie') {
        // For pie charts, count occurrences
        const counts = {};
        columnData.forEach(value => {
            if (value !== null && value !== undefined && value !== '') {
                counts[value] = (counts[value] || 0) + 1;
            }
        });
        
        const entries = Object.entries(counts).slice(0, 10); // Limit to top 10
        
        return {
            labels: entries.map(([key]) => key),
            datasets: [{
                data: entries.map(([, value]) => value),
                backgroundColor: colors.slice(0, entries.length)
            }]
        };
    } else {
        // For other chart types, use values directly or create histogram
        const numericData = columnData.filter(val => !isNaN(val) && val !== null && val !== undefined);
        
        if (numericData.length === 0) {
            // Handle non-numeric data
            const counts = {};
            columnData.slice(0, 10).forEach(value => {
                if (value !== null && value !== undefined && value !== '') {
                    counts[value] = (counts[value] || 0) + 1;
                }
            });
            
            return {
                labels: Object.keys(counts),
                datasets: [{
                    label: 'Count',
                    data: Object.values(counts),
                    backgroundColor: colors[0],
                    borderColor: colors[0],
                    borderWidth: 2
                }]
            };
        } else {
            // Use first 10 numeric values for simplicity
            const values = numericData.slice(0, 10);
            const labels = values.map((_, index) => `Item ${index + 1}`);
            
            return {
                labels: labels,
                datasets: [{
                    label: 'Value',
                    data: values,
                    backgroundColor: colors[0],
                    borderColor: colors[0],
                    borderWidth: 2,
                    fill: chartType === 'area'
                }]
            };
        }
    }
}

// Utility functions for data preview
function toggleDataView() {
    const toggleSwitch = document.getElementById('viewToggleSwitch');
    const toggleLabel = document.getElementById('toggleLabel');
    
    if (toggleSwitch && toggleLabel) {
        appState.viewMode = toggleSwitch.checked ? 'selected' : 'full';
        toggleLabel.textContent = toggleSwitch.checked ? 'Selected Columns View' : 'Full Dataset View';
        displayDataPreview();
    }
}

function searchColumns() {
    const searchInput = document.getElementById('columnSearch');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toLowerCase();
    const headers = document.querySelectorAll('#tableHeaders th');
    const columnsToShow = getColumnsToShow();
    
    headers.forEach((header, index) => {
        const columnName = columnsToShow[index];
        const shouldShow = columnName && columnName.toLowerCase().includes(searchTerm);
        
        // Hide/show column in table
        header.style.display = shouldShow ? '' : 'none';
        
        // Hide/show corresponding data cells
        const rows = document.querySelectorAll('#tableBody tr');
        rows.forEach(row => {
            const cell = row.children[index];
            if (cell) {
                cell.style.display = shouldShow ? '' : 'none';
            }
        });
    });
}

function togglePiiDetails() {
    const details = document.getElementById('piiDetails');
    const btn = document.getElementById('togglePiiDetails');
    
    if (details && btn) {
        details.classList.toggle('hidden');
        btn.textContent = details.classList.contains('hidden') ? 'Show Details' : 'Hide Details';
    }
}

function updateUploadStatus(status, text) {
    const indicator = document.getElementById('uploadStatus');
    const statusText = document.getElementById('statusText');
    
    if (indicator) {
        indicator.className = `status-indicator ${status}`;
    }
    if (statusText) {
        statusText.textContent = text;
    }
}

// Template and Customization Functions
function toggleTemplateType(type) {
    document.querySelectorAll('[data-template-type]').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`[data-template-type="${type}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    
    const predefinedDiv = document.getElementById('predefinedTemplates');
    const customDiv = document.getElementById('customTemplate');
    
    if (predefinedDiv) predefinedDiv.classList.toggle('hidden', type !== 'predefined');
    if (customDiv) customDiv.classList.toggle('hidden', type !== 'custom');
}

function selectTemplate(templateId) {
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('active');
    });
    
    const selectedCard = document.querySelector(`[data-template="${templateId}"]`);
    if (selectedCard) selectedCard.classList.add('active');
    
    appState.selectedTemplate = templateId;
    console.log(`Template selected: ${templateId}`);
}

function toggleAdvancedOptions() {
    const options = document.getElementById('advancedOptions');
    const btn = document.getElementById('toggleAdvanced');
    
    if (options && btn) {
        options.classList.toggle('hidden');
        btn.textContent = options.classList.contains('hidden') ? 'Show Options' : 'Hide Options';
    }
}

function generateInsights() {
    const queryInput = document.getElementById('llmQuery');
    if (!queryInput) return;
    
    const query = queryInput.value.trim();
    if (!query) {
        alert('Please enter a query for analysis');
        return;
    }
    
    showLoadingOverlay('Generating insights from your data...');
    
    setTimeout(() => {
        hideLoadingOverlay();
        alert('Custom insights generated and will be included in your presentation!');
        
        // Add custom insights to slides
        if (!appState.generatedSlides.find(slide => slide.title === 'Custom Insights')) {
            appState.generatedSlides.push({
                title: 'Custom Insights',
                type: 'AI Analysis',
                content: `<h2>Custom Analysis Results</h2><p><strong>Query:</strong> ${query}</p><div class="insights-content"><h3>Key Findings:</h3><ul><li>Pattern identified in the requested data analysis</li><li>Correlation discovered based on your specific query</li><li>Actionable insight derived from the analysis</li></ul></div>`
            });
            updateSlidesList();
        }
    }, 2500);
}

function handleCustomTemplateUpload(e) {
    const file = e.target.files[0];
    if (file) {
        console.log('Custom template uploaded:', file.name);
        alert(`Custom template "${file.name}" uploaded successfully!`);
    }
}

function handleLogoUpload(e) {
    const file = e.target.files[0];
    if (file) {
        console.log('Logo uploaded:', file.name);
        alert(`Logo "${file.name}" uploaded successfully!`);
    }
}

// Preview Functions
function generateInitialSlides() {
    appState.generatedSlides = [
        {
            title: 'Welcome',
            type: 'Introduction',
            content: '<h1>Welcome to DataPresenter</h1><p>Upload your data to generate a professional presentation</p><p class="subtitle">Your slides will appear here after data analysis</p>'
        }
    ];
    updateSlidesList();
}

function updateSlidesList() {
    const list = document.getElementById('slidesList');
    if (!list) return;
    
    list.innerHTML = '';
    
    appState.generatedSlides.forEach((slide, index) => {
        const div = document.createElement('div');
        div.className = `slide-item ${index === appState.currentSlide ? 'active' : ''}`;
        div.dataset.slide = index;
        div.innerHTML = `
            <div class="slide-thumbnail">${index + 1}</div>
            <div class="slide-info">
                <span class="slide-title">${slide.title}</span>
                <span class="slide-type">${slide.type}</span>
            </div>
        `;
        
        div.addEventListener('click', () => showSlide(index));
        list.appendChild(div);
    });
}

function showSlide(index) {
    if (index < 0 || index >= appState.generatedSlides.length) return;
    
    appState.currentSlide = index;
    
    // Update slide navigation
    document.querySelectorAll('.slide-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeSlideItem = document.querySelector(`[data-slide="${index}"]`);
    if (activeSlideItem) activeSlideItem.classList.add('active');
    
    // Update slide content
    const slide = appState.generatedSlides[index];
    const currentSlideEl = document.getElementById('currentSlide');
    if (currentSlideEl && slide) {
        currentSlideEl.innerHTML = slide.content;
    }
}

function updatePreview() {
    if (appState.generatedSlides.length === 1 && appState.processedData) {
        generateSlides();
    } else {
        showSlide(appState.currentSlide);
    }
}

function generateSlides() {
    if (!appState.processedData || appState.selectedColumns.size === 0) {
        console.log('No data or columns selected for slide generation');
        return;
    }
    
    const slides = [];
    
    // Title slide
    const title = appState.customSettings.title || `${appState.processedData.fileName} Analysis`;
    const company = appState.customSettings.companyName ? `<p class="company">${appState.customSettings.companyName}</p>` : '';
    
    slides.push({
        title: 'Title Slide',
        type: 'Introduction',
        content: `<h1>${title}</h1>${company}<p class="date">Generated on ${new Date().toLocaleDateString()}</p><p class="subtitle">Data-driven insights and analysis</p>`
    });
    
    // Dataset overview
    const nullCount = appState.processedData.data.reduce((count, row) => {
        return count + Object.values(row).filter(val => val === null || val === undefined || val === '').length;
    }, 0);
    const totalCells = appState.processedData.totalRows * appState.processedData.totalColumns;
    const completeness = Math.round(((totalCells - nullCount) / totalCells) * 100);
    
    slides.push({
        title: 'Dataset Overview',
        type: 'Overview',
        content: `
            <h2>Dataset Overview</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 30px 0;">
                <div style="background: var(--color-bg-1); padding: 20px; border-radius: var(--radius-base); text-align: center;">
                    <h3>${appState.processedData.totalRows.toLocaleString()}</h3>
                    <p>Total Rows</p>
                </div>
                <div style="background: var(--color-bg-2); padding: 20px; border-radius: var(--radius-base); text-align: center;">
                    <h3>${appState.processedData.totalColumns}</h3>
                    <p>Total Columns</p>
                </div>
                <div style="background: var(--color-bg-3); padding: 20px; border-radius: var(--radius-base); text-align: center;">
                    <h3>${appState.selectedColumns.size}</h3>
                    <p>Selected for Analysis</p>
                </div>
                <div style="background: var(--color-bg-4); padding: 20px; border-radius: var(--radius-base); text-align: center;">
                    <h3>${completeness}%</h3>
                    <p>Data Completeness</p>
                </div>
            </div>
            <p><strong>File:</strong> ${appState.processedData.fileName}</p>
        `
    });
    
    // Generate analysis-specific slides
    if (appState.selectedAnalysisType) {
        slides.push(...generateAnalysisSlides());
    }
    
    // Conclusion
    slides.push({
        title: 'Conclusion',
        type: 'Summary',
        content: `
            <h2>Conclusion</h2>
            <div class="conclusion-content">
                <p>This comprehensive analysis of <strong>${appState.processedData.fileName}</strong> has provided valuable insights into your data patterns and trends.</p>
                
                <h3>Key Takeaways:</h3>
                <ul>
                    <li>Analyzed ${appState.processedData.totalRows.toLocaleString()} records across ${appState.selectedColumns.size} key columns</li>
                    <li>Identified actionable insights for business optimization</li>
                    <li>Provided strategic recommendations based on data patterns</li>
                </ul>
                
                <p class="final-note">Continue to leverage data-driven insights for strategic decision-making and business growth.</p>
            </div>
        `
    });
    
    appState.generatedSlides = slides;
    updateSlidesList();
    console.log(`Generated ${slides.length} slides`);
}

function generateAnalysisSlides() {
    const slides = [];
    const configs = appState.chartConfigurations[appState.selectedAnalysisType];
    
    switch (appState.selectedAnalysisType) {
        case 'dashboard':
            const validDashboardConfigs = configs.filter(config => config && config.column);
            if (validDashboardConfigs.length > 0) {
                slides.push({
                    title: 'Dashboard Overview',
                    type: 'Dashboard',
                    content: `
                        <h2>Data Dashboard</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; height: 400px; margin: 20px 0;">
                            ${validDashboardConfigs.map((config, index) => 
                                `<div style="background: linear-gradient(135deg, #1f4e79, #4f81bd); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; text-align: center; padding: 10px;">
                                    <div>
                                        <div style="font-size: 24px; margin-bottom: 10px;">📊</div>
                                        <div>${config.column}</div>
                                        <div style="font-size: 12px; opacity: 0.8;">${config.chartType} chart</div>
                                    </div>
                                </div>`
                            ).join('')}
                        </div>
                    `
                });
            }
            break;
            
        case 'insights_charts':
            const validInsightsConfigs = configs.filter(config => config && config.column);
            validInsightsConfigs.forEach((config, index) => {
                slides.push({
                    title: `${config.column} Analysis`,
                    type: 'Analysis',
                    content: `
                        <h2>${config.column} Analysis</h2>
                        <div style="height: 250px; background: linear-gradient(135deg, #1f4e79, #4f81bd); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 20px 0; color: white; font-size: 18px; flex-direction: column;">
                            <div style="font-size: 48px; margin-bottom: 20px;">📈</div>
                            <div>${config.column} ${config.chartType.charAt(0).toUpperCase() + config.chartType.slice(1)} Chart</div>
                        </div>
                        <div class="analysis-insights">
                            <h3>Key Insights:</h3>
                            <ul>
                                <li>Statistical analysis reveals significant patterns in ${config.column} data</li>
                                <li>Trend analysis indicates ${Math.random() > 0.5 ? 'positive' : 'stable'} performance</li>
                                <li>Data shows ${Math.random() > 0.5 ? 'strong' : 'moderate'} correlation with business metrics</li>
                            </ul>
                        </div>
                    `
                });
            });
            break;
            
        case 'insights_only':
            if (configs.columns && configs.columns.length > 0) {
                slides.push({
                    title: 'Data Insights',
                    type: 'Text Analysis',
                    content: `
                        <h2>Comprehensive Data Analysis</h2>
                        <div class="text-analysis">
                            <h3>Statistical Summary:</h3>
                            <p>Analysis of ${configs.columns.length} selected columns reveals important business patterns and opportunities for optimization.</p>
                            
                            <h3>Key Findings:</h3>
                            <ul>
                                ${configs.columns.slice(0, 3).map(column => 
                                    `<li><strong>${column}:</strong> Shows ${Math.random() > 0.5 ? 'consistent' : 'variable'} patterns with potential for improvement</li>`
                                ).join('')}
                            </ul>
                            
                            <h3>Business Impact:</h3>
                            <p>These insights provide a foundation for data-driven decision making and strategic planning.</p>
                            
                            <h3>Selected Columns:</h3>
                            <p>${configs.columns.join(', ')}</p>
                        </div>
                    `
                });
            }
            break;
            
        case 'comparison':
            if (configs.xAxis && configs.yAxis) {
                slides.push({
                    title: `${configs.xAxis} vs ${configs.yAxis}`,
                    type: 'Comparison',
                    content: `
                        <h2>Comparative Analysis</h2>
                        <h3>${configs.xAxis} vs ${configs.yAxis}</h3>
                        <div style="height: 300px; background: linear-gradient(135deg, #9bb559, #759B37); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 30px 0; color: white; font-size: 18px; flex-direction: column;">
                            <div style="font-size: 48px; margin-bottom: 20px;">⚖️</div>
                            <div>${configs.xAxis} vs ${configs.yAxis}</div>
                            <div style="font-size: 14px; opacity: 0.8; margin-top: 10px;">${configs.chartType} visualization</div>
                        </div>
                        <div class="comparison-insights">
                            <p><strong>Correlation:</strong> ${(Math.random() * 0.8 + 0.2).toFixed(2)} correlation coefficient</p>
                            <p><strong>Relationship:</strong> ${Math.random() > 0.5 ? 'Positive' : 'Moderate'} relationship identified between variables</p>
                            <p><strong>Chart Type:</strong> ${configs.chartType.charAt(0).toUpperCase() + configs.chartType.slice(1)} chart selected for optimal visualization</p>
                        </div>
                    `
                });
            }
            break;
    }
    
    return slides;
}

function adjustZoom(delta) {
    appState.zoomLevel = Math.max(50, Math.min(200, appState.zoomLevel + delta));
    
    const slideContent = document.getElementById('currentSlide');
    if (slideContent) {
        slideContent.style.transform = `scale(${appState.zoomLevel / 100})`;
    }
    
    const zoomLevelEl = document.getElementById('zoomLevel');
    if (zoomLevelEl) {
        zoomLevelEl.textContent = `${appState.zoomLevel}%`;
    }
}

function toggleFullscreen() {
    const slidePreview = document.getElementById('slidePreview');
    if (slidePreview) {
        if (!document.fullscreenElement) {
            slidePreview.requestFullscreen().catch(console.error);
        } else {
            document.exitFullscreen().catch(console.error);
        }
    }
}

// Download Functions
function updateDownloadMetrics() {
    const slidesCount = appState.generatedSlides.length;
    let chartsCount = 0;
    
    if (appState.selectedAnalysisType) {
        const configs = appState.chartConfigurations[appState.selectedAnalysisType];
        switch (appState.selectedAnalysisType) {
            case 'dashboard':
                chartsCount = configs.filter(config => config && config.column).length;
                break;
            case 'insights_charts':
                chartsCount = configs.filter(config => config && config.column).length;
                break;
            case 'comparison':
                chartsCount = configs.xAxis && configs.yAxis ? 1 : 0;
                break;
            case 'insights_only':
                chartsCount = 0;
                break;
        }
    }
    
    const fileSize = (slidesCount * 0.3 + chartsCount * 0.1 + 0.5).toFixed(1);
    
    const elements = {
        slideCount: document.getElementById('slideCount'),
        chartCount: document.getElementById('chartCount'),
        fileSize: document.getElementById('fileSize'),
        downloadSlideCount: document.getElementById('downloadSlideCount'),
        downloadChartCount: document.getElementById('downloadChartCount'),
        downloadFileSize: document.getElementById('downloadFileSize'),
        analyzedColumns: document.getElementById('analyzedColumns'),
        generationTime: document.getElementById('generationTime'),
        finalTitle: document.getElementById('finalTitle'),
        thumbnailTitle: document.getElementById('thumbnailTitle'),
        creationDate: document.getElementById('creationDate')
    };
    
    const title = appState.customSettings.title || 
                  (appState.processedData ? `${appState.processedData.fileName} Analysis` : 'Data Analysis Presentation');
    
    // Update all metric displays
    if (elements.slideCount) elements.slideCount.textContent = `${slidesCount} slides`;
    if (elements.chartCount) elements.chartCount.textContent = `${chartsCount} charts`;
    if (elements.fileSize) elements.fileSize.textContent = `${fileSize} MB`;
    if (elements.downloadSlideCount) elements.downloadSlideCount.textContent = slidesCount;
    if (elements.downloadChartCount) elements.downloadChartCount.textContent = chartsCount;
    if (elements.downloadFileSize) elements.downloadFileSize.textContent = `${fileSize} MB`;
    if (elements.analyzedColumns) elements.analyzedColumns.textContent = appState.selectedColumns.size;
    if (elements.generationTime) elements.generationTime.textContent = '2.3s';
    if (elements.finalTitle) elements.finalTitle.textContent = title;
    if (elements.thumbnailTitle) elements.thumbnailTitle.textContent = title;
    if (elements.creationDate) elements.creationDate.textContent = `Created ${new Date().toLocaleDateString()}`;
}

function downloadPresentation() {
    if (appState.generatedSlides.length === 0) {
        alert('Please upload and analyze data first to generate slides');
        return;
    }
    
    showLoadingOverlay('Generating PowerPoint presentation...');
    
    setTimeout(() => {
        hideLoadingOverlay();
        
        const content = generatePresentationContent();
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const fileName = appState.customSettings.title || 'data-presentation';
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.txt`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        addToExportHistory('PPTX', new Date(), '2.4 MB');
        alert('Presentation downloaded! (Demo version: Text file with slide content)');
    }, 3000);
}

function downloadAsPDF() {
    if (appState.generatedSlides.length === 0) {
        alert('Please upload and analyze data first to generate slides');
        return;
    }
    
    showLoadingOverlay('Generating PDF export...');
    
    setTimeout(() => {
        hideLoadingOverlay();
        
        const content = generatePresentationContent().replace('POWERPOINT EXPORT', 'PDF EXPORT');
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const fileName = appState.customSettings.title || 'data-presentation';
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName.replace(/[^a-z0-9]/gi, '-').toLowerCase()}-pdf.txt`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        addToExportHistory('PDF', new Date(), '1.8 MB');
        alert('PDF export completed! (Demo version: Text file with content)');
    }, 2000);
}

function generatePresentationContent() {
    let content = `DATAPRESENTER - POWERPOINT EXPORT\n`;
    content += `=====================================\n\n`;
    content += `Title: ${appState.customSettings.title || 'Data Analysis Presentation'}\n`;
    content += `Company: ${appState.customSettings.companyName || 'N/A'}\n`;
    content += `Template: ${appState.selectedTemplate}\n`;
    content += `Analysis Type: ${appState.selectedAnalysisType || 'N/A'}\n`;
    content += `Generated: ${new Date().toLocaleString()}\n\n`;
    
    appState.generatedSlides.forEach((slide, index) => {
        content += `SLIDE ${index + 1}: ${slide.title}\n`;
        content += `Type: ${slide.type}\n`;
        content += `${'-'.repeat(40)}\n`;
        content += `${slide.content.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()}\n\n`;
    });
    
    if (appState.processedData) {
        content += `\nDATA SOURCE INFORMATION:\n`;
        content += `File: ${appState.processedData.fileName}\n`;
        content += `Total Rows: ${appState.processedData.totalRows}\n`;
        content += `Total Columns: ${appState.processedData.totalColumns}\n`;
        content += `Selected Columns: ${Array.from(appState.selectedColumns).join(', ')}\n`;
        content += `Analysis Type: ${appState.selectedAnalysisType}\n`;
        content += `PII Columns Detected: ${Array.from(appState.piiColumns).join(', ') || 'None'}\n`;
        
        if (appState.selectedAnalysisType) {
            content += `\nCHART CONFIGURATIONS:\n`;
            const configs = appState.chartConfigurations[appState.selectedAnalysisType];
            content += JSON.stringify(configs, null, 2);
        }
    }
    
    return content;
}

function addToExportHistory(format, date, size) {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;
    
    // Remove "no history" message
    const noHistory = historyList.querySelector('.no-history');
    if (noHistory) {
        noHistory.remove();
    }
    
    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML = `
        <div class="history-item-info">
            <div class="history-item-name">${format} Export</div>
            <div class="history-item-meta">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</div>
        </div>
        <div class="history-item-actions">
            <span style="margin-right: 10px; color: var(--color-text-secondary);">${size}</span>
            <button class="btn btn--outline btn--sm" onclick="redownload('${format}', '${date.getTime()}')">Re-download</button>
        </div>
    `;
    
    // Insert at the beginning
    historyList.insertBefore(item, historyList.firstChild);
}

function redownload(format, timestamp) {
    alert(`Re-downloading ${format} export from ${new Date(parseInt(timestamp)).toLocaleDateString()}`);
    // In a real app, this would trigger the actual download
}

function clearExportHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;
    
    historyList.innerHTML = '<p class="no-history">No previous exports</p>';
}

// Utility Functions
function showLoadingOverlay(text) {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    
    if (loadingText) loadingText.textContent = text;
    if (overlay) overlay.classList.remove('hidden');
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('hidden');
}

function sortTable(column) {
    console.log('Sorting by:', column);
    // In a real implementation, this would sort the data
    alert(`Sorting by ${column} (feature implemented in full version)`);
}

// Global event handlers for dynamic content
document.addEventListener('click', function(e) {
    // Add all suggestions button
    if (e.target.matches('#addAllSuggestions')) {
        e.preventDefault();
        document.querySelectorAll('.suggestion-item .suggestion-name').forEach(item => {
            const column = item.textContent;
            addSuggestionToAnalysis(column);
        });
        alert('All suggested columns added to analysis!');
    }
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    initializeApp();
});