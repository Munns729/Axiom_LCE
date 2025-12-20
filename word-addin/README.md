# Axiom Word Add-in (Test)

This is a simple proof-of-concept Word Add-in to demonstrate the "Headless" Linter/IDE capability.

## Prerequisites

- Node.js / npm
- Microsoft Word (Windows/Mac/Web)

## How to Run

1.  **Serve the Taskpane**
    The manifest points to `https://localhost:8080`. You need to serve the `src` directory with HTTPS.
    
    You can use `http-server`:
    ```bash
    npx http-server ./src --ssl --cors -p 8080
    ```
    *(Note: You might need to trust the self-signed certificate in your browser by opening https://localhost:8080/taskpane.html first)*.

2.  **Sideload the Manifest**
    - **Word on Web**: Go to Insert > Add-ins > Minimize the dialog > Upload My Add-in > Select `manifest.xml`.
    - **Word on Windows**: [Follow Microsoft Sideloading Instructions](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/create-a-network-shared-folder-catalog-for-task-pane-and-content-add-ins). (Easiest is often just "Share a folder" or use the Web version).

3.  **Run the Backend**
    Make sure your Rails and Python backend are running:
    ```bash
    docker compose up
    ```
    (Ensure Rails is on port 3000 and the Python backend on 8000).

## Usage

1.  Open the Add-in in Word (Axiom tab or button).
2.  Type your "Commercial Intent" (Playbook) in the text area (JSON format).
    *   *Example: `{ "governing_law": "New York" }`*
3.  Click "Verify Logic".
4.  The Add-in will send the document content to your local Axiom Cloud and display any logic warnings (e.g., if the document says "Delaware" but you requested "New York").
