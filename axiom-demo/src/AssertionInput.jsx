import React, { useState } from 'react';
import './AssertionInput.css';

/**
 * AssertionInput Component
 * 
 * Allows users to type natural language assertions about their contract
 * and verify them in real-time against the document logic.
 */
const AssertionInput = ({ onVerify, isVerifying, documentId }) => {
    const [assertion, setAssertion] = useState('');

    const examplePrompts = [
        "Founder keeps shares if Good Reason",
        "Tenant can terminate without penalty",
        "Warranty claims are capped at purchase price",
        "Employee retains vested stock on termination",
        "Indemnity survives for 2 years after closing"
    ];

    const handleSubmit = (e) => {
        e.preventDefault();
        if (assertion.trim() && !isVerifying) {
            onVerify(assertion.trim());
        }
    };

    const handleExampleClick = (example) => {
        setAssertion(example);
    };

    const handleKeyDown = (e) => {
        // Submit on Ctrl+Enter or Cmd+Enter
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            handleSubmit(e);
        }
    };

    return (
        <div className="assertion-input-container">
            <div className="assertion-input-header">
                <h3>Verify Business Assertion</h3>
                <p className="assertion-input-subtitle">
                    Type what you <em>expect</em> the contract to say, and we'll verify if it actually does.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="assertion-input-form">
                <div className="assertion-textarea-wrapper">
                    <textarea
                        className="assertion-textarea"
                        value={assertion}
                        onChange={(e) => setAssertion(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="e.g., Founder keeps shares if Good Reason..."
                        disabled={isVerifying || !documentId}
                        rows={3}
                    />
                    <div className="assertion-input-hint">
                        {!documentId ? (
                            <span className="hint-warning">⚠️ Upload a document first</span>
                        ) : (
                            <span className="hint-normal">
                                Press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to verify
                            </span>
                        )}
                    </div>
                </div>

                <button
                    type="submit"
                    className="assertion-submit-btn"
                    disabled={!assertion.trim() || isVerifying || !documentId}
                >
                    {isVerifying ? (
                        <>
                            <span className="spinner"></span>
                            Verifying...
                        </>
                    ) : (
                        <>
                            <span className="verify-icon">✓</span>
                            Verify Assertion
                        </>
                    )}
                </button>
            </form>

            <div className="assertion-examples">
                <div className="examples-header">Example Assertions:</div>
                <div className="examples-grid">
                    {examplePrompts.map((example, idx) => (
                        <button
                            key={idx}
                            className="example-chip"
                            onClick={() => handleExampleClick(example)}
                            disabled={isVerifying || !documentId}
                        >
                            {example}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AssertionInput;
