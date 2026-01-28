Office.onReady((info) => {
    if (info.host === Office.HostType.Word) {
        document.getElementById("run").onclick = run;
    }
});

async function run() {
    const statusDiv = document.getElementById("status");
    const resultsDiv = document.getElementById("results");
    const statsDiv = document.getElementById("stats");

    statusDiv.className = "loading";
    statusDiv.innerText = "Reading document...";
    resultsDiv.innerHTML = "";
    statsDiv.style.display = "none";

    // 1. Get entire document
    Office.context.document.getFileAsync(Office.FileType.Compressed, { sliceSize: 65536 }, function (result) {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
            const myFile = result.value;
            statusDiv.className = "loading";
            statusDiv.innerText = `Document read. ${myFile.sliceCount} slices. Processing...`;

            // 2. Read all slices
            getFileContent(myFile).then((docBlob) => {
                statusDiv.className = "loading";
                statusDiv.innerText = "Sending to Axiom API...";

                // 3. Send to API
                const playbook = document.getElementById("playbook").value;

                const formData = new FormData();
                formData.append("file", docBlob, "document.docx");
                formData.append("playbook", playbook);

                fetch("http://localhost:3000/analyze_logic", {
                    method: "POST",
                    body: formData
                })
                    .then(response => response.json())
                    .then(data => {
                        statusDiv.className = "success";
                        statusDiv.innerText = `Analysis complete! Contract ID: ${data.contract_id}`;
                        renderWarnings(data.warnings);
                        myFile.closeAsync();
                    })
                    .catch(err => {
                        statusDiv.className = "error";
                        statusDiv.innerText = "Error: " + err.message + ". Make sure Docker services are running.";
                        console.error(err);
                        myFile.closeAsync();
                    });

            }).catch(err => {
                statusDiv.innerText = "Error reading slices: " + err.message;
                myFile.closeAsync();
            });
        } else {
            statusDiv.className = "error";
            statusDiv.innerText = "Error: " + result.error.message;
        }
    });
}

function getFileContent(myFile) {
    return new Promise((resolve, reject) => {
        let slicesReceived = 0;
        let sliceCount = myFile.sliceCount;
        let docBytes = [];

        // Helper to process slice
        function getSlice(i) {
            myFile.getSliceAsync(i, function (result) {
                if (result.status === Office.AsyncResultStatus.Succeeded) {
                    // result.value.data is an array of bytes (integer array in IE, Uint8Array otherwise?)
                    // The docs say "The data property of the slice object returns the raw data of the file slice."
                    // It returns a byte array.

                    docBytes[i] = result.value.data;
                    slicesReceived++;

                    if (slicesReceived === sliceCount) {
                        // Assemble
                        // Flatten array of arrays
                        let params = [];
                        for (let j = 0; j < sliceCount; j++) {
                            params = params.concat(docBytes[j]); // Note: might be slow for huge docs- optimization needed later
                        }

                        // Create Blob
                        // Make sure params is a typed array for Blob constructor if needed, or straight array
                        const uint8Array = new Uint8Array(params);
                        const blob = new Blob([uint8Array], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
                        resolve(blob);
                    } else {
                        getSlice(i + 1);
                    }
                } else {
                    reject(result.error);
                }
            });
        }

        getSlice(0);
    });
}

function renderWarnings(warnings) {
    const resultsDiv = document.getElementById("results");
    const statsDiv = document.getElementById("stats");

    if (!warnings || warnings.length === 0) {
        resultsDiv.innerHTML = "<div class='no-warnings'>No conflicts detected - document matches playbook!</div>";
        statsDiv.style.display = "none";
        return;
    }

    // Calculate statistics
    const highCount = warnings.filter(w => w.severity === "High").length;
    document.getElementById("warningCount").textContent = warnings.length;
    document.getElementById("highSeverity").textContent = highCount;
    statsDiv.style.display = "block";

    // Render warnings
    resultsDiv.innerHTML = "";
    warnings.forEach(w => {
        const severityClass = w.severity === "High" ? "warning-high" :
            w.severity === "Medium" ? "warning-medium" : "warning-low";
        const severityBadgeClass = w.severity.toLowerCase();

        const div = document.createElement("div");
        div.className = `warning ${severityClass}`;
        div.innerHTML = `
            <div class="warning-header">
                <div class="warning-title">${w.issue}</div>
                <span class="warning-severity ${severityBadgeClass}">${w.severity}</span>
            </div>
            <div class="warning-snippet">${w.text_snippet}</div>
            ${w.remediation ? `<div class="warning-remediation">${w.remediation}</div>` : ''}
        `;
        resultsDiv.appendChild(div);
    });
}

function loadExamplePlaybook() {
    document.getElementById("playbook").value = `{
  "governing_law": "New York",
  "payment_terms": "30 days",
  "liability_cap": "$1,000,000"
}`;
}
