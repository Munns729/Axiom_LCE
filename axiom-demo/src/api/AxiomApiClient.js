/**
 * AxiomApiClient.js
 * Handles communication with the Rails Backend (Orchestrator).
 */

const BASE_URL = 'http://localhost:3000';

class AxiomApiClient {
    /**
     * Uploads a .docx file to the backend for ingestion.
     * @param {File} file - The file object from the input.
     * @returns {Promise<Object>} - The JSON response containing contract_id.
     */
    static async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        return response.json();
    }

    /**
     * Retrieves the parsed AST (Tree) for a given contract.
     * @param {string} contractId 
     * @returns {Promise<Object>} - The generic AST/JSON structure.
     */
    static async getContractTree(contractId) {
        const response = await fetch(`${BASE_URL}/contract/${contractId}/tree`);

        if (!response.ok) {
            throw new Error('Failed to fetch contract tree');
        }

        return response.json();
    }

    /**
     * Runs a RAG query against the contract.
     * @param {string} contractId 
     * @param {string} queryText 
     * @returns {Promise<Object>} - The answer/results.
     */
    static async queryContract(contractId, queryText) {
        const response = await fetch(`${BASE_URL}/contract/${contractId}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: queryText })
        });

        if (!response.ok) {
            throw new Error('Query failed');
        }

        return response.json();
    }
}

export default AxiomApiClient;
