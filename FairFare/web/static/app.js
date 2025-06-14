// State management
let participants = [];
let currentSession = null;

// Add state for current expense being edited
let currentExpenseId = null;

// UI Functions
function showStep(stepNumber) {
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.add('hidden');
    document.getElementById(`step${stepNumber}`).classList.remove('hidden');
}

function addParticipant() {
    const input = document.getElementById('participantName');
    const name = input.value.trim();

    if (name && !participants.includes(name)) {
        participants.push(name);
        updateParticipantList();
        input.value = '';
    }
}

function updateParticipantList() {
    const list = document.getElementById('participantList');
    list.innerHTML = participants.map(name => `
        <div class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full flex items-center">
            ${name}
            <button onclick="removeParticipant('${name}')" class="ml-2 text-indigo-600 hover:text-indigo-800">×</button>
        </div>
    `).join('');
}

function removeParticipant(name) {
    participants = participants.filter(p => p !== name);
    updateParticipantList();
}

// API Functions
async function initializeSession() {
    const names = participants;
    if (names.length === 0) {
        alert('Please add at least one participant');
        return;
    }

    try {
        const response = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ names })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to initialize session');
        }

        const data = await response.json();
        currentSession = data;
        showStep(2);
        updatePayerList();
        updateSplitUI();
        updateExpenseRecords();
    } catch (error) {
        alert(error.message);
    }
}

function addPayer() {
    const payerList = document.getElementById('payerList');
    const payerDiv = document.createElement('div');
    payerDiv.className = 'flex gap-2 items-center';

    // Get already selected payers
    const selectedPayers = Array.from(document.querySelectorAll('#payerList select'))
        .map(select => select.value);

    // Filter out already selected payers
    const availablePayers = participants.filter(name => !selectedPayers.includes(name));

    if (availablePayers.length === 0) {
        alert('All participants have already been added as payers');
        return;
    }

    payerDiv.innerHTML = `
        <select class="flex-1 p-2 border rounded" onchange="updatePayerOptions(this)">
            ${availablePayers.map(name => `<option value="${name}">${name}</option>`).join('')}
        </select>
        <input type="number" step="0.01" min="0" placeholder="Amount"
               class="w-32 p-2 border rounded">
        <button onclick="removePayer(this)"
                class="text-red-600 hover:text-red-800">×</button>
    `;
    payerList.appendChild(payerDiv);
}

function removePayer(button) {
    const payerDiv = button.parentElement;
    payerDiv.remove();
    // Update options in all remaining payer selects
    document.querySelectorAll('#payerList select').forEach(select => {
        updatePayerOptions(select);
    });
}

function updatePayerOptions(select) {
    const selectedPayers = Array.from(document.querySelectorAll('#payerList select'))
        .map(s => s.value);

    // Get all options except the current select's value
    const otherSelectedPayers = selectedPayers.filter(name => name !== select.value);

    // Update options in all selects
    document.querySelectorAll('#payerList select').forEach(s => {
        const currentValue = s.value;
        s.innerHTML = participants
            .filter(name => !otherSelectedPayers.includes(name) || name === currentValue)
            .map(name => `<option value="${name}" ${name === currentValue ? 'selected' : ''}>${name}</option>`)
            .join('');
    });
}

function updatePayerList() {
    const payerList = document.getElementById('payerList');
    payerList.innerHTML = '';
    addPayer(); // Add first payer by default
}

function updateSplitUI() {
    const splitMethod = document.getElementById('splitMethod').value;
    const splitOptions = document.getElementById('splitOptions');

    switch (splitMethod) {
        case 'even':
            splitOptions.innerHTML = `
                <div class="space-y-2">
                    <label class="block text-gray-700">Select participants to split between:</label>
                    <div class="flex flex-wrap gap-2">
                        ${participants.map(name => `
                            <label class="flex items-center space-x-2">
                                <input type="checkbox" value="${name}" checked>
                                <span>${name}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            `;
            break;

        case 'exact':
            splitOptions.innerHTML = `
                <div class="space-y-2">
                    <label class="block text-gray-700">Enter exact amounts:</label>
                    ${participants.map(name => `
                        <div class="flex items-center gap-2">
                            <span class="w-24">${name}:</span>
                            <input type="number" data-name="${name}" step="0.01" min="0"
                                   class="flex-1 p-2 border rounded"
                                   placeholder="Amount">
                        </div>
                    `).join('')}
                </div>
            `;
            break;

        case 'ratio':
            splitOptions.innerHTML = `
                <div class="space-y-2">
                    <label class="block text-gray-700">Enter ratios (should sum to 1):</label>
                    ${participants.map(name => `
                        <div class="flex items-center gap-2">
                            <span class="w-24">${name}:</span>
                            <input type="number" data-name="${name}" step="0.01" min="0" max="1"
                                   class="flex-1 p-2 border rounded"
                                   placeholder="Ratio">
                        </div>
                    `).join('')}
                </div>
            `;
            break;
    }
}

function addExpenseRecord(payment) {
    const recordsDiv = document.getElementById('expenseRecords');
    const recordDiv = document.createElement('div');
    recordDiv.className = 'bg-gray-50 p-3 rounded hover:bg-gray-100 transition';
    recordDiv.dataset.id = payment.id;  // Add data-id attribute
    recordDiv.innerHTML = `
        <div class="flex justify-between items-start">
            <div class="flex-1 cursor-pointer" onclick="loadExpenseForEdit(${JSON.stringify(payment).replace(/"/g, '&quot;')})">
                <div class="font-medium">${payment.description}</div>
                <div class="text-sm text-gray-600">
                    Paid by: ${Object.entries(payment.participant_contributions)
                        .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                        .join(', ')}
                </div>
                <div class="text-sm text-gray-600">
                    Split: ${payment.split_method.replace('_', ' ')}
                </div>
                <div class="text-sm text-gray-600">Input shares: ${Object.entries(payment.input_participant_shares)
                    .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                    .join(', ')}</div>
                <div class="text-sm text-gray-600">Final shares: ${Object.entries(payment.split_participant_shares)
                    .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                    .join(', ')}</div>
            </div>
            <button onclick="deleteExpense('${payment.id}')"
                    class="text-red-600 hover:text-red-800 ml-2 px-2 py-1 rounded hover:bg-red-100">
                ×
            </button>
        </div>
    `;
    recordsDiv.appendChild(recordDiv);
}

function loadExpenseForEdit(payment) {
    currentExpenseId = payment.id;

    // Set description
    document.getElementById('expenseDescription').value = payment.description;

    // Set payers
    const payerList = document.getElementById('payerList');
    payerList.innerHTML = '';
    Object.entries(payment.participant_contributions).forEach(([name, amount]) => {
        const payerDiv = document.createElement('div');
        payerDiv.className = 'flex gap-2 items-center';
        payerDiv.innerHTML = `
            <select class="flex-1 p-2 border rounded" onchange="updatePayerOptions(this)">
                ${participants.map(p => `<option value="${p}" ${p === name ? 'selected' : ''}>${p}</option>`).join('')}
            </select>
            <input type="number" step="0.01" min="0" placeholder="Amount"
                   class="w-32 p-2 border rounded" value="${amount}">
            <button onclick="removePayer(this)"
                    class="text-red-600 hover:text-red-800">×</button>
        `;
        payerList.appendChild(payerDiv);
    });

    // Set split method and update UI
    const splitMethodSelect = document.getElementById('splitMethod');
    splitMethodSelect.value = payment.split_method;

    // Force a UI update for the split method
    updateSplitUI();

    // After UI is updated, set the split configuration
    if (payment.split_method === 'even') {
        // Wait for the DOM to update with the new split options
        requestAnimationFrame(() => {
            const checkboxes = document.querySelectorAll('#splitOptions input[type="checkbox"]');
            checkboxes.forEach(cb => {
                // Check if the participant has a share in the input_participant_shares
                cb.checked = payment.input_participant_shares[cb.value] !== undefined;
            });
        });
    } else if (payment.split_method === 'exact' || payment.split_method === 'ratio') {
        const inputs = document.querySelectorAll('#splitOptions input[type="number"]');
        inputs.forEach(input => {
            const name = input.dataset.name;
            input.value = payment.input_participant_shares[name] || '';
        });
    }
}

function newExpense() {
    currentExpenseId = null;
    resetExpenseForm();
}

function saveExpense() {
    const description = document.getElementById('expenseDescription').value.trim();
    if (!description) {
        alert('Please enter a description');
        return;
    }

    // Get payers and amounts
    const payers = Array.from(document.querySelectorAll('#payerList select')).map(select => select.value);
    const amounts = Array.from(document.querySelectorAll('#payerList input')).map(input => parseFloat(input.value) || 0);

    if (payers.length === 0 || amounts.some(isNaN)) {
        alert('Please enter valid payer information');
        return;
    }

    // Get split method and shares
    const splitMethod = document.getElementById('splitMethod').value;
    let shares = [];
    let shareAmounts = [];

    if (splitMethod === 'even') {
        const checkboxes = document.querySelectorAll('#splitOptions input[type="checkbox"]:checked');
        shares = Array.from(checkboxes).map(cb => cb.value);
        shareAmounts = shares.map(() => 0); // Use 0 for even split
    } else if (splitMethod === 'exact' || splitMethod === 'ratio') {
        const inputs = document.querySelectorAll('#splitOptions input[type="number"]');
        inputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            if (value > 0) {
                shares.push(input.dataset.name);
                shareAmounts.push(value);
            }
        });
    }

    if (shares.length === 0) {
        alert('Please select at least one participant for splitting');
        return;
    }

    // Validate total for exact split
    if (splitMethod === 'exact') {
        const totalPaid = amounts.reduce((sum, amount) => sum + amount, 0);
        const totalShared = shareAmounts.reduce((sum, amount) => sum + amount, 0);
        if (Math.abs(totalPaid - totalShared) > 0.01) {
            alert(`Total paid (${totalPaid.toFixed(2)}) must equal total shared (${totalShared.toFixed(2)})`);
            return;
        }
    }

    // Validate ratios sum to 1 for ratio split
    if (splitMethod === 'ratio') {
        const totalRatio = shareAmounts.reduce((sum, ratio) => sum + ratio, 0);
        if (Math.abs(totalRatio - 1) > 0.01) {
            alert(`Ratios must sum to 1 (current sum: ${totalRatio.toFixed(2)})`);
            return;
        }
    }

    const data = {
        id: currentExpenseId,
        description,
        payers,
        amounts,
        shares,
        share_amounts: shareAmounts,
        split_method: splitMethod
    };

    fetch('/api/add_payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        resetExpenseForm();
        updateExpenseRecords();
    })
    .catch(error => {
        alert(error.message);
    });
}

function resetExpenseForm() {
    // Reset description
    document.getElementById('expenseDescription').value = '';

    // Reset payer list to default state
    const payerList = document.getElementById('payerList');
    payerList.innerHTML = '';
    const payerDiv = document.createElement('div');
    payerDiv.className = 'flex gap-2 items-center';
    payerDiv.innerHTML = `
        <select class="flex-1 p-2 border rounded" onchange="updatePayerOptions(this)">
            ${participants.map(name => `<option value="${name}">${name}</option>`).join('')}
        </select>
        <input type="number" step="0.01" min="0" placeholder="Amount"
               class="w-32 p-2 border rounded">
        <button onclick="removePayer(this)"
                class="text-red-600 hover:text-red-800">×</button>
    `;
    payerList.appendChild(payerDiv);

    // Reset split method to default
    document.getElementById('splitMethod').value = 'even';
    updateSplitUI();
}

async function settle() {
    try {
        const response = await fetch('/api/settle');
        if (!response.ok) {
            throw new Error('Failed to get settlement');
        }

        const data = await response.json();

        // Update net balances
        const netBalances = document.getElementById('netBalances');
        netBalances.innerHTML = Object.entries(data.net_balances)
            .map(([name, balance]) => `
                <div class="flex justify-between items-center p-2 ${balance >= 0 ? 'bg-green-100' : 'bg-red-100'} rounded">
                    <span>${name}</span>
                    <span class="font-semibold">${balance.toFixed(2)}</span>
                </div>
            `).join('');

        // Update transactions
        const transactions = document.getElementById('transactions');
        if (data.transactions.length === 0) {
            transactions.innerHTML = '<p class="text-gray-600">No settlements needed!</p>';
        } else {
            transactions.innerHTML = data.transactions
                .map(tx => `
                    <div class="flex justify-between items-center p-2 bg-indigo-100 rounded">
                        <span>${tx.from} pays ${tx.to}</span>
                        <span class="font-semibold">${tx.amount.toFixed(2)}</span>
                    </div>
                `).join('');
        }

        // Remove any existing payment records section
        const existingRecords = document.getElementById('paymentRecordsSection');
        if (existingRecords) {
            existingRecords.remove();
        }

        // Add payment records section
        const paymentRecords = document.createElement('div');
        paymentRecords.id = 'paymentRecordsSection';
        paymentRecords.className = 'mt-6';
        paymentRecords.innerHTML = `
            <div class="flex justify-between items-center mb-2">
                <h3 class="text-xl font-semibold">Payment Records</h3>
                <button onclick="togglePaymentRecords()"
                        class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                    Show Records
                </button>
            </div>
            <div id="paymentRecords" class="hidden space-y-2"></div>
        `;
        transactions.parentElement.appendChild(paymentRecords);

        showStep(3);
    } catch (error) {
        alert(error.message);
    }
}

function togglePaymentRecords() {
    const recordsDiv = document.getElementById('paymentRecords');
    const button = recordsDiv.previousElementSibling.querySelector('button');

    if (recordsDiv.classList.contains('hidden')) {
        // Show records
        recordsDiv.classList.remove('hidden');
        button.textContent = 'Hide Records';

        // Fetch and display payment records
        fetch('/api/payments')
            .then(response => response.json())
            .then(payments => {
                recordsDiv.innerHTML = payments.map(payment => `
                    <div class="bg-white p-4 rounded shadow">
                        <div class="font-semibold mb-2">${payment.description}</div>
                        <div class="text-sm text-gray-600 space-y-1">
                            <div>Paid by: ${Object.entries(payment.participant_contributions)
                                .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                                .join(', ')}</div>
                            <div>Split: ${payment.split_method}</div>
                            <div>Input shares: ${Object.entries(payment.input_participant_shares)
                                .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                                .join(', ')}</div>
                            <div>Final shares: ${Object.entries(payment.split_participant_shares)
                                .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                                .join(', ')}</div>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => {
                recordsDiv.innerHTML = '<p class="text-red-600">Failed to load payment records</p>';
            });
    } else {
        // Hide records
        recordsDiv.classList.add('hidden');
        button.textContent = 'Show Records';
    }
}

function resetSession() {
    console.log("Resetting session...");

    // Clear participants
    participants = [];
    currentSession = null;

    // Reset form
    document.getElementById('participantList').innerHTML = '';
    const nameInput = document.getElementById('participantName');
    if (nameInput) nameInput.value = '';

    // Reset expense records
    document.getElementById('expenseRecords').innerHTML = '';
    currentExpenseId = null;

    // Reset expense form
    resetExpenseForm();

    // Reset settlement results
    document.getElementById('netBalances').innerHTML = '';
    document.getElementById('transactions').innerHTML = '';

    // Show step 1
    if (typeof showStep === 'function') {
        showStep(1);
    } else {
        console.warn('showStep() is not defined');
    }
}

async function deleteExpense(paymentId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }

    try {
        const response = await fetch(`/api/payments/${paymentId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete expense');
        }

        // Remove the record from the UI
        const record = document.querySelector(`#expenseRecords [data-id="${paymentId}"]`);
        if (record) {
            record.remove();
        }

        // If we're currently editing this expense, reset the form
        if (currentExpenseId === paymentId) {
            resetExpenseForm();
            currentExpenseId = null;
        }
    } catch (error) {
        alert(error.message);
    }
}

function updateExpenseRecords() {
    fetch('/api/payments')
        .then(response => response.json())
        .then(payments => {
            const recordsDiv = document.getElementById('expenseRecords');
            recordsDiv.innerHTML = ''; // Clear existing records

            payments.forEach(payment => {
                const recordDiv = document.createElement('div');
                recordDiv.className = 'bg-gray-50 p-3 rounded hover:bg-gray-100 transition';
                recordDiv.dataset.id = payment.id;
                recordDiv.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div class="flex-1 cursor-pointer" onclick="loadExpenseForEdit(${JSON.stringify(payment).replace(/"/g, '&quot;')})">
                            <div class="font-medium">${payment.description}</div>
                            <div class="text-sm text-gray-600">
                                Paid by: ${Object.entries(payment.participant_contributions)
                                    .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                                    .join(', ')}
                            </div>
                            <div class="text-sm text-gray-600">
                                Split: ${payment.split_method.replace('_', ' ')}
                            </div>
                            <div class="text-sm text-gray-600">Input shares: ${Object.entries(payment.input_participant_shares)
                                .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                                .join(', ')}</div>
                            <div class="text-sm text-gray-600">Final shares: ${Object.entries(payment.split_participant_shares)
                                .map(([name, amount]) => `${name} (${amount.toFixed(2)})`)
                                .join(', ')}</div>
                        </div>
                        <button onclick="deleteExpense('${payment.id}')"
                                class="text-red-600 hover:text-red-800 ml-2 px-2 py-1 rounded hover:bg-red-100">
                            ×
                        </button>
                    </div>
                `;
                recordsDiv.appendChild(recordDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching payments:', error);
            alert('Failed to update expense records');
        });
}
