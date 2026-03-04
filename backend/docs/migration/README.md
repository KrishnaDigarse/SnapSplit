# SnapSplit Migration Documentation

Detailed documentation for each phase of the backend migration from **Python/FastAPI** to **Java/Spring Boot**.

## Phases

| Phase | Status | Document |
|---|---|---|
| Phase 0 — Project Scaffolding | ✅ Complete | [phase0_scaffolding.md](phase0_scaffolding.md) |
| Phase 1 — Entities & Repositories | 🔲 Pending | [phase1_entities.md](phase1_entities.md) |
| Phase 2 — Security & Auth | 🔲 Pending | phase2_security.md |
| Phase 3 — Core APIs & Services | 🔲 Pending | phase3_core_apis.md |
| Phase 4 — AI Pipeline | 🔲 Pending | phase4_ai_pipeline.md |
| Phase 5 — Async & WebSocket | 🔲 Pending | phase5_async_websocket.md |
| Phase 6 — Middleware & Cross-Cutting | 🔲 Pending | phase6_middleware.md |
| Phase 7 — Testing | 🔲 Pending | phase7_testing.md |
| Phase 8 — Cutover & Cleanup | 🔲 Pending | phase8_cutover.md |

## How to Read

Each phase document contains:
1. **Objective** — what this phase accomplishes
2. **Python → Spring Boot Mapping** — side-by-side comparison of the old and new code
3. **Files Created** — every file with its purpose
4. **Code Walkthrough** — detailed explanation of each file's logic
5. **Key Decisions** — design choices and why they were made
6. **How to Run / Verify** — commands to build and test
