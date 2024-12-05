let allData = [];

const commandHeaders = {
    common: ['Command Type', 'Agent', 'Target', 'Alert', 'Interface', 'Connectivity', 'CPU', 'Memory', 'Avg Latency', 'Stdev Latency', 'Jitter', 'Bandwidth', 'Loss', 'TX Bytes', 'TX Packets', 'RX Bytes', 'RX Packets', 'Timestamp'],
};

function getTasks() {
    return fetch('/tasks')
        .then(response => response.json())
        .catch(error => {
            console.error('Error fetching tasks:', error);
            return []; 
        });
}

function populateTable(data) {
    const dataTableBody = document.getElementById('dataTableBody');
    const tableHeaderRow = document.getElementById('tableHeaderRow');
    dataTableBody.innerHTML = ''; 
    tableHeaderRow.innerHTML = ''; 

    if (data.length === 0) {
        console.warn('No data available to populate.');
        return;
    }

    const headers = [...commandHeaders.common];

    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        console.log(th)
        tableHeaderRow.appendChild(th);
    });

    data.forEach(item => {
        const row = document.createElement('tr');
        if (item.is_alert) {
            row.style.color = 'red';
        }

        appendCell(row, item.command_type); 
        appendCell(row, item.agent);
        appendCell(row, item.target);
        appendCell(row, item.is_alert ? 'Yes' : 'No');
        appendCell(row, item.interface_name || '-');
        appendCell(row, item.connectivity || '-');
        appendCell(row, item.cpu || '-');
        appendCell(row, item.memory || '-');
        appendCell(row, item.avg_latency || '-');
        appendCell(row, item.stdev_latency || '-');
        appendCell(row, item.jitter || '-');
        appendCell(row, item.bandwidth || '-');
        appendCell(row, item.loss || '-');
        appendCell(row, item.tx_bytes || '-');
        appendCell(row, item.tx_packets || '-');
        appendCell(row, item.rx_bytes || '-');
        appendCell(row, item.rx_packets || '-');
        appendCell(row, new Date(item.timestamp * 1000).toLocaleString());

        dataTableBody.appendChild(row);
    });
}

function appendCell(row, text) {
    const cell = document.createElement('td');
    cell.textContent = text || '-';
    row.appendChild(cell);
}

function filterTable() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const filteredData = allData.filter(item =>
        item.agent.toLowerCase().includes(query) ||
        item.target.toLowerCase().includes(query) ||
        item.command_type.toLowerCase().includes(query)
    );

    populateTable(filteredData);
}

document.addEventListener('DOMContentLoaded', () => {
    getTasks().then(data => {
        allData = data;
        populateTable(allData);
    });

    document.getElementById('searchInput').addEventListener('input', filterTable);
});
