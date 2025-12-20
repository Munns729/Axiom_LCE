# Axiom MVP Run Instructions

1. **Build Containers**
   ```powershell
   docker compose build
   ```

2. **Start System**
   ```powershell
   docker compose up
   ```

3. **Verify**
   - Rails Health: http://localhost:3000/up
   - Spine Health: http://localhost:8000/docs
   - Upload: `POST http://localhost:3000/upload` (form-data: file=@doc.docx)

## Architecture
- **Rails (3000)**: API Orchestrator. Proxies logic to Spine.
- **Spine (8000)**: Document Engine (Python). In-memory AST.
- **Postgres (5432)**: Ready for persistence.
- **Redis (6379)**: Ready for background jobs.
