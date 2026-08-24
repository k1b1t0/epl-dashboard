# 🎼 Orchestration Module Documentation

## 📌 Overview
Briefly describe the Orchestration setup using Kestra to schedule and automate the end-to-end Data Pipeline (Setup -> Ingestion -> PySpark Load -> dbt Transform).

---

## ⚙️ Architecture & Features
- **Orchestrator**: Kestra Standalone Server
- **Task Runner**: `io.kestra.plugin.core.runner.Process`
- **Schedule Trigger**: Daily at 06:00 UTC (`0 6 * * *`)
- **Error Handling & Retry**: Exponential backoff retry on Ingestion task & failure alerts.

---

## 🔑 Key Files
- `epl_pipeline.yml`: Complete Kestra Flow definition.

---

## 📝 Trigger Execution via CLI / API
```bash
curl -u "admin@kestra.io:Admin1234!" -X POST http://localhost:8080/api/v1/executions/football/epl_pipeline
```
