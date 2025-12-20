# Axiom - The "IDE for Transactions"

**Axiom** is an Assurance & Origination Platform designed for Transactional Leaders. It functions as a true **Integrated Development Environment (IDE) for legal contracts**, decoupling Business Intent (Outcomes) from Legal Syntax (Text).

> **Core Philosophy**: "Test-Driven Development (TDD) for Legal Contracts."

## 🚀 Vision

Axiom treats commercial intent as the "Axiom"—a self-evident truth—and the legal contract as the proof. The system provides "Logic Warnings" rather than legal advice, verifying that the written contract logically supports the intended commercial position.

## 🔑 Key Features

### 1. The "Verification Loop"
A streaming interaction model that provides immediate feedback:
- **Assertion**: Users state a business outcome (e.g., "Founder keeps shares if Good Reason").
- **Analysis**: The system indexes clauses and compares logic in real-time.
- **Visual Trace**: Logic conflicts are highlighted with visual "Logic Circuits" showing causality (e.g., *Good Reason -> Bad Leaver -> Forfeiture*).

### 2. "Shadow Akoma" Ingestion
A robust document ingestion pipeline:
- Ingests messy `.docx` files.
- Maps visual hierarchy to a "loose" Akoma Ntoso structure (LegalDocML).
- Creates a "Virtual DOM" of the contract for manipulation while preserving the original file's "skeleton" for perfect round-trip export.

### 3. Berty (AI Copilot)
An intelligent assistant for:
- **Q&A**: Answer questions about contract contents (e.g., "Is there a Non-Compete?").
- **Ad-Hoc Drafting**: Rewrite sections based on natural language prompts.

## 🛠️ Technical Architecture

Axiom follows a **Container-First** deployment model, suitable for both SaaS and On-Premise Air-Gapped environments.

- **App Server**: Ruby on Rails 8 (API Mode) - Orchestrator & Logic Stream.
- **Document Engine ("Spine")**: Python (FastAPI) + `python-docx` - XML Manipulation & AST Parsing.
- **Database**: PostgreSQL + `pgvector` for vector storage.
- **Background Jobs**: Redis + Sidekiq.
- **Frontend**: React-based UI (demonstrated in `axiom-demo` and `rails_app` views).

## 📦 Project Structure

- `rails_app/`: Main application server (Rails).
- `backend/` / `spine/`: Python microservices for document parsing and analysis.
- `axiom-demo/`: Frontend demonstration.
- `db/`: Database initialization and configuration.
- `tests/`: Test suites and corpus data.

## 🏁 Getting Started

### Prerequisites
- Docker & Docker Compose
- Git

### Installation & Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/Munns729/Axiom_LCE.git
   cd Axiom_LCE
   ```

2. **Build and Start Services**
   ```bash
   docker compose build
   docker compose up
   ```

3. **Verify Deployment**
   - **Rails Health**: [http://localhost:3000/up](http://localhost:3000/up)
   - **Spine/Backend Health**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Verification Commands
To test the ingestion pipeline locally (requires Python environment if not using Docker):
```bash
# Example for testing the Python backend
cd backend
pytest
```

## 📄 License
Proprietary & Confidential.
