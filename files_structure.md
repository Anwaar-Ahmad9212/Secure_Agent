# 📁 Complete Directory File Structure

This document provides an exhaustive index of all files and folders located within `files_3` and its subdirectories, detailing the exact purpose of every single file.

---

## 🗂️ Overall Architecture Highlights

- **`ai_agent/`**: Contains the code that orchestrates the Large Language Model (LLM), parses its inputs, and provides tools for it to run.
- **`dashboard/`**: Housing for the web-based monitoring interface and frontend views.
- **`n8n/`**: Setup documentation and workflows for the n8n automation pipeline logic.
- **`security/`**: The primary security proxy middleware. Contains rule enforcers, semantic similarity detectors, logging APIs, and model-building scripts.
- **`security_proxy_v2/`**: An evolved version of the security interceptor utilizing a sophisticated risk-scoring engine with multiple detector sub-modules.
- **`vector_db/`**: Holds internal ChromaDB files enabling similarity-search-based input validation.

---

## 📄 Root Directory (`/files_3/`)
### Documentation
- **`ARCHITECTURE.md`**: Outlines system design, request flow, component orchestration schemes, and the theoretical foundation for the security proxy logic.
- **`File_structure.md`**: A legacy document outlining the older setup instructions and assumed file arrangements.
- **`files_structure.md`**: (This file) A highly detailed generated breakdown of the current environment.
- **`GETTING_STARTED.md`**: Step-by-step tutorial on building the environment and launching components locally.
- **`PROJECT_SUMMARY.md`**: Defines project objectives, summarizing how the AI Agent Security demo demonstrates prompt injection defense.
- **`QUICKSTART.md`**: A fast-track setup guide avoiding theoretical elements to simply run the required Python services.
- **`README.md`**: The repository’s main welcome page, containing standard introduction, features, and core setup instructions.
- **`TEST_SCENARIOS.md`**: Lists common cyber threat scenarios (e.g., prompt leakage, SQLi) to practically test via the demo UI.
- **`windows.md`**: Explains troubleshooting and dependency resolution specific to Windows distributions.

### Launch & Administration Scripts
- **`start_demo.bat` / `start_demo.sh`**: Start all services correctly on Windows or Unix respectively (Security Proxy, Logger, and AI App server).
- **`stop_demo.bat` / `stop_demo.sh`**: Safely terminating all demo background processes natively.
- **`start.bat` / `stop.bat`**: Alternate launchers targeting generic service instantiations.
- **`run_tests.sh`**: Wrapper script executing the integration test loops natively.
- **`verify.bat`**: Validates the Python version, `Pip` packages, and available ports on Windows systems prior to executing the app.

### Root Application Scripts & Data
- **`agent_app.py`**: Legacy or duplicate root-level entry point exposing the Agent endpoints globally. 
- **`logger.py`**: Intercepts event data and records them synchronously avoiding race conditions.
- **`logs.json`**: Temporary output log store holding generic events globally.
- **`requirements.txt`**: Standard python package manifest needed for running the root web servers.
- **`rules.json`**: Globally mapped rules dictating keyword bans and regex blocks.
- **`security_proxy.py`**: Legacy or duplicate version of the security reverse-proxy service natively running in root.
- **`tools.py`**: Provides accessible operations available for execution by the AI payload (Simulating file deletion, external calls etc).
- **`workflow.json`**: Standard JSON logic exported specifically to interface with automation APIs easily.
- **`index.html`**: A root-level static webpage to serve as a fast entry dashboard when needed.

---

## 🤖 AI Agent (`/files_3/ai_agent/`)
This module handles all operations related to processing AI requests.
- **`agent_app.py`**: The main execution engine. Accepts external requests, passes instructions dynamically through Ollama (or other LLM), fetches reasoning paths, and triggers any tools requested dynamically.
- **`config.json`**: System definitions explicitly structuring the AI behavior, setting its allowed LLM capabilities and temperature variants.
- **`database.py`**: Simulated mock Database layer containing schemas and data rows that the AI uses to simulate database query tasks.
- **`demo_database.db`**: Local SQLite database populated by `./database.py` with mock information (Users, sales, etc.) for testing real reads.
- **`test_ai_behaviour.py`**: A dedicated suite evaluating specifically if the AI correctly interprets edge-case scenarios or benign conversations.
- **`tools.py`**: Functional python definitions that the LLM is explicitly allowed to invoke as 'actions', for example, reading a mock file, executing a mock system command, or querying `demo_database.db`.

---

## 📊 Dashboard Site (`/files_3/dashboard/`)
Client-facing frontend user interface allowing visualization of intercepted attacks.
- **`COMPLETE_PROJECT_GUIDE.md`**: Comprehensive UI mapping, API architecture specifications, and styling definitions.
- **`index.html`**: Primary monitoring frontend to actively track and render charts showing blocked attempts, severity scores, and throughput.
- **`input.html` / `input_2.html` / `input_enhanced.html`**: Various iterations of the testing playground interface allowing users to write test prompts securely or natively to observe the difference visually.
- **`script.js`**: Core polling mechanism requesting real-time analytics from the local `logger.py` endpoint every few moments.
- **`style.css` / `style_new.css`**: Design tokens, transition logic, and flexbox configurations powering the visual interface.

---

## ⚡ n8n Workflows (`/files_3/n8n/`)
Configuration for integrating an external n8n environment into the demo logic.
- **`README.md`**: Guide outlining how to boot n8n externally and manually attach it sequentially to the pipeline.
- **`workflow.json`**: The encoded topological map of n8n nodes natively readable by their platform—essentially mimicking a production workflow triggering the AI dynamically.

---

## 🛡️ Security Engine (`/files_3/security/`)
Primary iteration of backend AI threat detection components. 
- **`build_comprehensive_dataset.py`**: Web-scraper and dataset assembler designed to aggregate thousands of open-source malicious prompt techniques securely.
- **`build_unified_vector.py`**: Conversion pipeline which processes raw malicious string templates, encodes them logically into embeddings, and saves them within `vector_db`.
- **`diaganose_semantic_detection.py`**: Quality assurance script designed to trace why specific vectors do or do not properly map similarities during a semantic payload check.
- **`enhanced_validator.py`**: An advanced iteration of validating inputs combining structural limits and strict regex.
- **`log_utils.py`**: Secondary helpers dealing natively with slicing logs, chunking timelines, or aggregating json responses.
- **`logger.py`**: API listening consistently mapping active threats into a JSON representation without blocking pipeline operations.
- **`logs.json`**: Stores array objects tracking exactly what time, IP, prompt, and rule was matched per interaction.
- **`rules.json`**: The actual static lookup dictionary dictating strict hardcoded rules mapping known phrases to "SQL INJECTION" or "RCE" outputs.
- **`security_proxy.py`**: Central gateway intercepts raw inputs, triggers sequential validation tests across tools, and ultimately accepts or drops an AI prompt.
- **`test_delete_file.py`**: Evaluator simulating a malicious external task explicitly verifying if it blocks system file destruction attempts correctly.
- **`test_prompts.py`**: Test script enumerating a static array of valid workflows vs malicious injections, checking that each handles ideally.
- **`vector_db_detector.py`**: Code natively instantiating `chromadb`, reading similarity boundaries, and providing boolean answers assessing proximity of unknown prompts mathematically against the database content.

---

## 🛡️ Security Engine V2 (`/files_3/security_proxy_v2/`)
Next generation middleware moving from basic block-lists to ensemble evaluation techniques mapping distinct scores into a unified AI `Risk`.
- **`QUICKSTART.md` / `README.md`**: Distinct explanations on setting up the v2 architectural dependencies uniquely.
- **`requirements.txt`**: ML-specific module requirements.
- **`security_proxy_v2.py`**: Engine execution gateway aggregating multiple detector scripts securely.
- **`config/detection_config.json`**: Numerical boundaries defining exactly where thresholds lie (e.g. at what ratio does an anomaly formally become critical).
- **`config/weights.json`**: Defines the weighted power of various detectors in the overall scoring.
- **`detectors/anomaly_detector.py`**: Mathematical string calculator calculating entropy or character frequencies to catch obfuscated/base64 encoded payloads.
- **`detectors/fuzzy_detector.py`**: Matches inputs via Levenshtein distance allowing it to capture misspelled bypass iterations like "1gn0re pr3vi0uz inztructshons".
- **`detectors/ml_classifier.py`**: A supervised Text Classification logic dynamically predicting the chance an input string maps to an attack category.
- **`detectors/risk_scorer.py`**: Responsible uniquely for summing, formatting, and presenting mathematical reasoning back to the top-level scripts dynamically based on all the others outputs.
- **`detectors/rule_detector.py`**: Refactored static rule checking isolated directly into a compliant module.
- **`detectors/vector_detector.py`**: Identical to V1's vector database detection but structured distinctly as an ensemble component.
- **`train/train_ml_model.py`**: Isolated pipeline fitting local input models allowing it to output serialized predictions required by `ml_classifier`.
- **`utils/feature_extractor.py`**: Function library cleaning text inputs by stripping spacing, calculating lengths, or standardizing syntax prior to ML evaluation logic.

---

## 🗄️ Vector Storage (`/files_3/vector_db/`)
- **`chroma.sqlite3`**: The natively generated ChromaDB local file which houses thousands of embedding multi-dimensional coordinates. This acts directly as the offline brain required by `vector_db_detector.py` safely comparing inputs mathematically in memory.
