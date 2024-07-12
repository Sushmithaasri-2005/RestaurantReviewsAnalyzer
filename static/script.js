const form = document.getElementById("uploadForm");
form.addEventListener("submit", async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const formData = new FormData();
    formData.append("file1", fileInput.files[0]);

    const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
    });

    const result = await response.json();
    console.log(result);
    form.style.display = 'none';

    if (result.message === "File saved successfully") {
        visualizeCSV();
    }
});

async function visualizeCSV() {
    const response = await fetch("http://localhost:8000/download");
    const title = document.getElementById("report_title");
    title.style.display = "block";
    const csvData = await response.text();
    const title1 = document.getElementById("bert_title");
    title1.style.display = "block";
    const bert = await fetch("http://localhost:8000/download_bert");
    const bertCsvData = await bert.text();

    // Parse the CSV data using PapaParse
    Papa.parse(csvData, {
        header: true, // If your CSV has headers
        complete: function(results) {
            const rows = results.data;
            const table = document.createElement("table");

            // Create table headers
            const headerRow = document.createElement("tr");
            const headers = Object.keys(rows[0]);
            headers.forEach(header => {
                const th = document.createElement("th");
                th.innerText = header;
                headerRow.appendChild(th);
            });
            table.appendChild(headerRow);

            // Create table rows
            rows.forEach(row => {
                const tr = document.createElement("tr");
                headers.forEach(header => {
                    const td = document.createElement("td");
                    td.innerText = row[header];
                    tr.appendChild(td);
                });
                table.appendChild(tr);
            });

            const csvTable = document.getElementById("csvTable");
            csvTable.innerHTML = "";
            csvTable.appendChild(table);

            // Count the number of 1s in each relevant column
            const counts = { food: 0, ambience: 0, price: 0, service: 0, "anecdotes/miscellaneous": 0 };
            rows.forEach(row => {
                Object.keys(counts).forEach(key => {
                    if (row[key] === "1.0" || row[key] === 1 || row[key] === "1") { // Handle different possible formats of 1
                        counts[key]++;
                    }
                });
            });

            generatePieChart(counts);
        },
        error: function(err) {
            console.error("Error parsing CSV:", err);
        }
    });

    Papa.parse(bertCsvData, {
        header: true, // If your CSV has headers
        complete: function(results) {
            const rows = results.data;
            const table = document.createElement("table");
    
            // Create table headers
            const headerRow = document.createElement("tr");
            const headers = Object.keys(rows[0]);
            headers.forEach(header => {
                const th = document.createElement("th");
                th.innerText = header;
                headerRow.appendChild(th);
            });
            table.appendChild(headerRow);
    
            // Create table rows
            rows.forEach(row => {
                const tr = document.createElement("tr");
                headers.forEach(header => {
                    const td = document.createElement("td");
                    td.innerText = row[header];
                    tr.appendChild(td);
                });
                table.appendChild(tr);
            });
    
            const csvTable = document.getElementById("sentiTable");
            const tableCaption = document.createElement('caption');
            tableCaption.innerHTML = "BERT report";
            csvTable.appendChild(tableCaption);
            csvTable.innerHTML = "";
            csvTable.appendChild(table);
    
            // Count the sentiment values for each column
            const sentimentCounts = {
                "Service Sentiment": { positive: 0, neutral: 0, negative: 0 },
                "Food Sentiment": { positive: 0, neutral: 0, negative: 0 },
                "Anecdotes Sentiment": { positive: 0, neutral: 0, negative: 0 },
                "Price Sentiment": { positive: 0, neutral: 0, negative: 0 },
                "Ambience Sentiment": { positive: 0, neutral: 0, negative: 0 }
            };
    
            rows.forEach(row => {
                Object.keys(sentimentCounts).forEach(key => {
                    // Ensure row[key] exists and is not undefined
                    const sentiment = (row[key] || "").toString().toLowerCase().trim();
                    if (sentimentCounts[key][sentiment] !== undefined) {
                        sentimentCounts[key][sentiment]++;
                    }
                });
            });
    
            generateBarChart(sentimentCounts);
        },
        error: function(err) {
            console.error("Error parsing CSV:", err);
        }
    });
    
}
function generatePieChart(counts) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    const data = {
        labels: Object.keys(counts),
        datasets: [{
            data: Object.values(counts),
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
        }]
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Counts of Each Category'
            }
        }
    };

    new Chart(ctx, {
        type: 'pie',
        data: data,
        options: options
    });
}

function generateBarChart(sentimentCounts) {
    const ctx = document.getElementById('barChart').getContext('2d');
    const labels = Object.keys(sentimentCounts);
    const sentimentTypes = ["positive", "neutral", "negative"];
    const backgroundColors = ['#4CAF50', '#FFC107', '#F44336']; // Colors for positive, neutral, negative

    const datasets = sentimentTypes.map((type, index) => ({
        label: type.charAt(0).toUpperCase() + type.slice(1),
        data: labels.map(label => sentimentCounts[label][type]),
        backgroundColor: backgroundColors[index],
        borderColor: backgroundColors[index],
        borderWidth: 1
    }));

    const data = {
        labels: labels,
        datasets: datasets
    };

    const options = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Sentiment Analysis of Reviews'
            }
        }
    };

    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
}
