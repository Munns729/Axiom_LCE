AXIOM (by Bertrand) – Master Specification & Agent Instructions

Version: 3.2 (Bertrand & Berty Rebrand)
Status: Ready for Agent Execution
Core Philosophy: "Test-Driven Development (TDD) for Legal Contracts."
Deployment Model: Container-First (SaaS or On-Prem Air-Gapped).

1. Executive Vision: The "IDE for Transactions"

Axiom (developed by Bertrand) is an Assurance & Origination Platform (SaaS Linter) for Transactional Leaders. It decouples Business Intent (Outcomes) from Legal Syntax (Text).

The Name: An Axiom is a statement that is self-evidently true. In our system, the Commercial Intent is the Axiom; the Contract is just the proof.

Liability Stance: The system is a tool, not a lawyer. It provides "Logic Warnings," not legal advice. (Strict Non-Reliance).

Privacy Stance: Zero-Retention Architecture. Deployable via Docker/K8s to client VPCs.

2. Product Specification

2.1 The "Verification Loop" (Streaming Interaction)

The Assertion (Input):

Actor: Commercial Lead.

Action: Types a business outcome (e.g., "Founder keeps shares if Good Reason").

The Stream (Processing):

System Action: Does NOT freeze. Immediately streams "Thought Tokens" to the UI.

Visuals: "Indexing Clauses... Found 'Bad Leaver' (Sec 4.2)... Comparing Logic..."

The Linter Result (Output):

Logic Conflict: "Potential Logic Mismatch detected in Section 4.2."

Visual: Red underline (like a syntax error in code).

The Visual Trace (The "Why"):

Action: User hovers over the conflict.

System Action: Displays the "Logic Circuit" overlay.

Visuals: A node-link diagram showing the chain of causality:

[Node: "Good Reason" Scenario] --(triggers)--> [Node: "Bad Leaver" Def] --(activates)--> [Node: Sec 4.2 Forfeiture].

This visually proves why the outcome is Red.

2.2 Origination & Ingestion (The Pipeline)

2.2.1 Path A: The "Generative Loop" (From Scratch)

Standard generation using ClauseLibrary and Playbook overrides.

2.2.2 Path B: The "Shadow Akoma" Ingestion (From External File) [CRITICAL]

Strategy: "Loose Akoma Ntoso (LegalDocML) Structure."

Concept: Use Akoma Ntoso vocabulary for the internal tree, but allow flexible JSON structures that tolerate messy Word formatting.

Upload: Ingest .docx / .pdf.

Parsing:

Step 1: Parse the .docx XML.

Step 2: Map the visual hierarchy to Akoma Ntoso Types:

h1/h2 -> article / chapter

p (numbered) -> section / paragraph

p (bulleted) -> point

p (plain) -> content / intro

Step 3: Store each Component as a ClauseNode with its an_type (Akoma Ntoso Type).

Manipulation (The IDE Behavior):

Update: Update text in Node X -> Replace XML content for Node X.

Add: Insert new Node Y -> Inject new <w:p> XML element after Node X, inheriting Node X's styling.

Merge: Combine content into Node X -> Delete Node Y XML element.

Integrity: The system creates a "Virtual DOM" of the contract. It only "renders" back to .docx when the user exports, ensuring the original file's "Skeleton" (Styles/Metadata) remains untouched.

2.3 Administrative Features: Playbook "Learning"

Upload: Admin uploads "Gold Standard" contracts.

Extraction: Engine extracts preferences (e.g., "Cap Indemnity at 1x").

Definition: System creates a Playbook configuration.

2.4 Berty (The AI Copilot)

This feature re-uses the Vector Store and AST for conversational interaction.

Location: Toggle in Left Panel ("Verify Mode" vs. "Ask Berty").

Capability A (Q&A):

Input: "Does this contract have a Non-Compete?"

Process: RAG Query against ClauseNode embeddings.

Output: "Yes, Section 8.1 contains a 12-month non-compete." (Clicking link scrolls Right Panel to Section 8.1).

Capability B (Ad-Hoc Drafting):

Input: "Hey Berty, rewrite Section 4 to be more founder-friendly."

Process: LLM generates text -> Document Microservice updates the AST Node for Section 4.

2.5 The Refactor Linter (Complexity Management)

A proactive system to keep the "Legal DOM" clean and atomic.

Trigger: The Clause Analysis engine detects "High Concept Density" in a single node (e.g., a 20-line paragraph containing both Vesting and Non-Compete obligations).

Visual Warning: Amber squiggly line under the paragraph. Tooltip: "Complexity Warning: This clause contains multiple distinct obligations."

Action: "Refactor Clause" button.

Process:

LLM proposes a split (e.g., Section 4.1 becomes 4.1(a) and 4.1(b)).

Document Microservice splits the XML node into two sibling nodes, applying the correct list numbering styles automatically.

The AST updates to show two distinct nodes, allowing for granular verification.

3. Technical Architecture (Container-First)

3.1 Stack Overview

App Server: Ruby on Rails 8 (API Mode).

Document Microservice: Python (FastAPI) + python-docx (XML Manipulation) + Custom AST Parser.

Database: PostgreSQL + pgvector.

Queues: Redis + Sidekiq (Background jobs).

Streaming: Rails ActionController::Live / SSE (Server-Sent Events).

Deployment: Dockerfile and docker-compose.yml included from Day 1.

3.2 Key Data Models

Contract (id, content_json, original_file_data).

ClauseNode (id, contract_id, parent_id, sibling_order, original_xml_id, text_content, embedding).

an_type: String (e.g., 'article', 'section', 'point' - aligned with Akoma Ntoso).

an_num: String (e.g., "4.1", "a" - the label).

an_heading: String (e.g., "Termination").

LogicTrace (id, scenario_id, steps_log).

4. Antigravity Agent Guidelines

Phase 1: The "Smoke Test" Demo (Interactive Prototype)

Goal: A React Artifact to demo the "Linting" and "Visual Trace" experience.

[COPY THIS INTO ANTIGRAVITY]

Role: Senior Frontend Engineer.
Context: Building the "Smoke Test" prototype for Axiom (by Bertrand).
Objective: Create InteractiveDealVerifier.jsx.
Design Changes:

Branding: Update the header to say AXIOM (Terminal Font) // Berty AI v1.0.

Streaming Simulation: When "Run Verification" is clicked, show a log appearing line-by-line ("Parsing Sec 4...", "Checking Definitions...") to simulate the latency handling.

Linter Aesthetic: Instead of a big "FAIL" card, use a "Warning" style (Yellow/Red underline in text).

The Logic Circuit: Add a "Show Trace" button on the Warning. When clicked, overlay a simple SVG connecting line or flowchart node that visualizes: [Scenario] -> [Definition: Bad Leaver] -> [Section 4.2].

Content: Use the "Bad Leaver" trap scenario.

Phase 2: R&D Parsing Spike (The "Deep Dive")

Goal: Prove we can ingest a messy Word Doc without breaking it.

[COPY THIS INTO ANTIGRAVITY]

Role: Python ML Engineer.
Task: Create a "Document Ingestion Playground".
Tech: Python, python-docx, langchain.
Objectives:
0.  Infrastructure (Golden Corpus): Create a tests/corpus directory. Create a pytest fixture that iterates through every file in this directory. Any parser logic you write MUST pass a "Read/Write" test on all files in this directory before you mark the task complete.

Ingest: Script that accepts a .docx file.

Akoma Ntoso Mapping: Build a Tree representation (AST) of the document.

Use Akoma Ntoso vocabulary for the nodes (article, section, paragraph, point).

Do not validate against the strict XSD schema. Build a flexible JSON Tree.

Map each node to its original_xml_id.

Vectorize: Store these nodes in a local vector store (ChromaDB).

Structural Edit Test:

Test A (Injection): Insert a new paragraph Node between Clause 4.1 and 4.2.

Test B (Refactor Split): Take Clause 4.2 (a dense paragraph), split its text into two logical parts, and rewrite the Docx to replace the single paragraph with two new numbered items (4.2.1 and 4.2.2). Verify the XML structure holds.

Round-Trip: Save the modified tree back to .docx and verify it opens in Word with perfect formatting.

Phase 3: The MVP Build (Rails + Containerization)

Goal: The Ship-ready Backend.

[COPY THIS INTO ANTIGRAVITY]

Role: Systems Architect.
Task: Initialize Axiom Backend with Docker Support.
Checklist:

Dockerize: Create Dockerfile for Rails 8 and docker-compose for Postgres/Redis.

Constraint (Air-Gap): Configure config/storage.yml to use Disk (local storage) by default. Do not configure AWS S3. We are building for on-premise deployment.

Streaming: Configure Rails for Server-Sent Events (SSE) to handle the Logic Stream.

Microservice Connection: Set up a simple HTTP Client in Rails to talk to the (future) Python Document Service.