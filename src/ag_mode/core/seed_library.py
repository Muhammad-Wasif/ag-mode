"""Mode Library Seeder.

Generates the complete initial library of 70+ modes with modular markdown files
and writes modes/modes.json registry index.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def generate_library(modes_root: Path) -> None:
    modes_root.mkdir(parents=True, exist_ok=True)

    catalog: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # 1. WEB DEVELOPMENT MODE (Deep modular files as requested)
    # -------------------------------------------------------------
    web_dir = modes_root / "web"
    web_dir.mkdir(parents=True, exist_ok=True)

    web_files = {
        "README.md": """# Web Development Mode
Operates as a high-performing full-lifecycle web engineering team.
Enforces modular architecture, responsive UI/UX, strict security protocols, and quality gates.
""",
        "core.md": """# Core Web Engineering Principles
1. **Separation of Concerns**: Decouple UI, state, domain logic, and data access.
2. **Framework Selection**: Choose frameworks based on project requirements (e.g. Next.js for SSR/SEO, Vite/React for SPA, Astro for content-heavy sites). Never assume one stack fits all.
3. **Resilience**: Graceful error boundaries, offline readiness where appropriate, resilient network handling.
""",
        "architecture.md": """# Web Architecture
- **Client-Side vs Server-Side**: Determine rendering strategy (CSR, SSR, SSG, ISR) by requirement.
- **State Management**: Prefer local state > lifted state > global store (Zustand, Redux, Pinia, Context).
- **API Communication**: Type-safe client queries (TanStack Query, Axios, RTK Query).
""",
        "frontend.md": """# Frontend Standards
- Semantic HTML5 elements (`<header>`, `<main>`, `<nav>`, `<article>`, `<section>`, `<footer>`).
- Clean modern CSS / Vanilla CSS or Tailwind depending on project requirements.
- Responsive design: Mobile-first viewport break-points (sm: 640px, md: 768px, lg: 1024px, xl: 1280px).
- Zero uncaught Promise rejections or console errors.
""",
        "backend.md": """# Backend Standards
- Layered architecture: Controllers -> Services -> Repositories -> Models.
- Stateless REST or GraphQL APIs with clean HTTP status codes (200, 201, 400, 401, 403, 404, 422, 500).
- Input validation on all incoming request payloads before business logic execution.
""",
        "database.md": """# Database Architecture
- Relational (PostgreSQL, MySQL, SQLite) for ACID transactions, structured relational entities.
- Document/NoSQL (MongoDB, Redis) for caches, sessions, unstructured documents.
- Always use migrations (Prisma, Alembic, Drizzle, TypeORM, Knex). Never alter production schemas manually.
- Index foreign keys and frequently queried filters.
""",
        "api.md": """# API Design
- RESTful conventions: Resource-oriented URLs, appropriate HTTP verbs.
- OpenAPI / Swagger documentation for all external endpoints.
- Rate limiting headers and pagination (`limit`, `offset`, or cursor-based) for collection queries.
""",
        "security.md": """# Web Security Directives
- **SQL / NoSQL Injection**: Mandatory parameterized queries and ORM escaping.
- **XSS**: Strict output encoding, Content Security Policy (CSP), avoid `dangerouslySetInnerHTML` / `innerHTML`.
- **CSRF**: SameSite cookies, CSRF tokens on state-changing requests.
- **Headers**: Helmet / security headers (`Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`).
- **Secrets**: Never commit `.env` or credentials. Use environment variables.
""",
        "authentication.md": """# Authentication
- Passwords hashed with bcrypt (work factor >= 12) or Argon2id.
- JWTs: Short-lived access tokens (15m) with refresh token rotation stored in HttpOnly, Secure, SameSite cookies.
- Support OAuth2 / OpenID Connect and MFA (TOTP) where required.
""",
        "authorization.md": """# Authorization & Access Control
- Role-Based Access Control (RBAC) or Attribute-Based Access Control (ABAC).
- Verify permissions at the service layer, not solely in UI route guards.
- Tenant isolation: enforce tenant ID filters on every database query for multi-tenant applications.
""",
        "ui-ux.md": """# UI/UX Design Engine
- **Visual Languages**: Match design system to industry context:
  * Corporate/Enterprise: Clean typography, neutral backgrounds, subtle borders, high information density.
  * Modern SaaS: Crisp typography (Inter, Outfit), refined contrast, subtle shadows, intuitive micro-interactions.
  * Editorial / Content: Generous line height, readable serif or modern sans, content-first layout.
  * Banking / Medical: High contrast, strict accessibility, reassuring visual stability, no chaotic decorative elements.
- **Consistency**: Maintain a unified 4px/8px spatial grid throughout margin and padding.
""",
        "responsive-design.md": """# Responsive Design Guidelines
- Mobile-first approach: test 360px, 390px, 768px, 1024px, 1440px.
- Fluid typography using `clamp()` where appropriate.
- Touch target sizes minimum 44x44px on mobile devices.
- Prevent horizontal scrollbars (`overflow-x: hidden` / robust flex/grid layouts).
""",
        "accessibility.md": """# Accessibility (a11y)
- WCAG 2.1 AA compliance minimum.
- Color contrast ratio >= 4.5:1 for normal text, 3:1 for large text.
- Full keyboard navigability (visible focus indicators, Tab order, Enter/Space/Escape behaviors).
- ARIA landmarks, `aria-label`, `aria-expanded`, and descriptive `alt` attributes for images.
""",
        "performance.md": """# Web Performance Optimization
- Core Web Vitals: LCP < 2.5s, FID/INP < 200ms, CLS < 0.1.
- Image optimization: WebP/AVIF formats, responsive `srcset`, lazy loading for below-the-fold media.
- Code splitting and dynamic imports for heavy components.
""",
        "testing.md": """# Testing Standards
- Unit testing: Jest / Vitest for business logic and utility functions.
- Component testing: React Testing Library / Vue Test Utils.
- Integration / End-to-End: Playwright / Cypress for critical user paths (auth, checkout, form submission).
""",
        "debugging.md": """# Debugging & Error Handling
- Comprehensive error boundary components on frontend.
- Centralized error middleware on backend with structured JSON error responses:
  `{"status": "error", "code": "RESOURCE_NOT_FOUND", "message": "...", "details": []}`
- No raw stack traces exposed to client in production mode.
""",
        "error-handling.md": """# Error Handling Protocols
- Catch errors at boundaries, log detailed context internally, return sanitized user-friendly messages.
- Distinguish between expected domain errors (validation) and unexpected system faults.
""",
        "deployment.md": """# Deployment & DevOps
- Containerization: Multi-stage Dockerfiles for lean production images.
- CI/CD pipelines: Lint -> Test -> Security Scan -> Build -> Deploy.
- Health check endpoints (`/healthz`, `/readyz`).
""",
        "seo.md": """# SEO Best Practices
- Single canonical `<h1>` per page.
- Comprehensive `<meta>` tags: title, description, Open Graph, Twitter Cards, robots.
- Automated `sitemap.xml` and `robots.txt` generation.
""",
        "project-types.md": """# Project-Type Intelligence
Automatically detect and apply specialized architectures based on request:
- E-Commerce: Cart, Stripe/PayPal checkout, inventory synchronization, order management.
- LMS: Courses, lessons, quizzes, progress tracking, certificates, instructor/student roles.
- Library Management: Book catalog, circulation, borrowing/returns, fines, reservations.
- Hospital Management: Appointments, patient medical records, doctor rosters, privacy compliance.
- SaaS Platform: Multitenancy, Stripe subscriptions, team invitations, usage limits.
""",
        "ecommerce.md": """# E-Commerce Architecture
- Customer: Registration, Catalog, Search, Filtering, Cart, Checkout, Order Tracking.
- Admin: Products, Categories, Stock/Inventory, Orders, Discounts, Analytics.
- Backend: Idempotent payment processing, webhook listeners, atomic stock decrement.
""",
        "lms.md": """# Learning Management System (LMS)
- Roles: Superadmin, Instructor, Student, Auditor.
- Features: Video/text lessons, quizzes with automatic grading, progress persistence, certificates.
""",
        "library-management.md": """# Library Management System
- Catalog with ISBN indexing, status (Available, Borrowed, Reserved, Lost).
- Borrowing records, due dates, automated overdue fee calculations.
""",
        "hospital-management.md": """# Hospital Management System
- Patient demographics, medical history, appointment scheduling, doctor availability.
- Strict confidentiality, audit logs for all medical record reads and edits.
""",
        "dashboard.md": """# Dashboard Architecture
- Executive overview: KPIs, metric summary cards, interactive charts, date range filtering.
- Data tables with sorting, filtering, pagination, and CSV export.
""",
        "saas.md": """# SaaS Architecture
- Tenant separation, role-based member management, Stripe webhook billing integration.
- Feature gating based on active subscription tier.
""",
        "anti-ai-patterns.md": """# Anti "AI-Generated Website" Rules
DO NOT produce generic low-quality AI aesthetic:
- ❌ NO random purple-to-blue gradients on every card and background.
- ❌ NO useless floating glowing neon blobs.
- ❌ NO emoji used as professional company logos.
- ❌ NO fake testimonials with stock names like 'John Doe, CEO of TechCorp'.
- ❌ NO giant empty hero sections with zero substance.
- ❌ NO excessive animations that distract from content.
- ✔️ Produce crisp, purpose-driven UI designed like a professional product team.
""",
        "logo-standards.md": """# Brand Identity & Logo Standards
- Never use an emoji or a single letter inside a colored circle as a logo.
- Create authentic vector SVG logos with balanced typography and meaningful brand marks.
- Support responsive variations: Full horizontal logo, compact icon/favicon, light mode, and dark mode variants.
""",
        "tools.md": """# Web Development Tooling
- Frontend: Next.js, React, Vue.js, Svelte, TypeScript, Vite.
- Backend: Node.js, Express, NestJS, FastAPI, Django, Go.
- Database: PostgreSQL, Redis, SQLite, Prisma ORM, Drizzle.
- Testing: Vitest, Playwright, Jest.
- Tooling evaluation: Select tools based on project size, latency requirements, and maintainability.
""",
        "quality-gate.md": """# Web Quality Gate
- [ ] Responsive layout validated across mobile, tablet, and desktop viewports
- [ ] Zero unhandled JavaScript / TypeScript runtime errors
- [ ] All forms validate inputs on both frontend and backend
- [ ] Passwords and secrets not exposed in client bundle or repository
- [ ] Semantic HTML and accessibility contrast verified
- [ ] Automated tests pass with zero critical failures
""",
    }

    for fname, content in web_files.items():
        with open(web_dir / fname, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

    catalog.append({
        "id": "web",
        "name": "Web Development",
        "category": "Development",
        "description": "Full-lifecycle professional web development with strict UI/UX, security, and quality gates.",
        "version": "1.0.0",
        "dependencies": [],
        "tags": ["web", "frontend", "backend", "fullstack", "react", "nextjs", "vue", "html", "css", "javascript", "typescript"],
        "directory": "web",
        "files": list(web_files.keys()),
        "quality_gates": [
            "Responsive layout verified on mobile, tablet, desktop",
            "Zero uncaught client or server errors",
            "Input validation and parameterized queries",
            "No secrets in client bundle",
            "Semantic HTML and WCAG AA accessibility",
        ],
        "security_profile": {
            "injection_defense": "Parameterized queries mandatory",
            "xss_defense": "Strict output encoding and CSP",
            "csrf_defense": "SameSite cookies & CSRF tokens",
        },
    })

    # Helper function to generate standardized mode directories
    def add_mode(
        mode_id: str,
        name: str,
        category: str,
        description: str,
        tags: List[str],
        dependencies: List[str],
        core_guidelines: str,
        tools_content: str,
        quality_gates: List[str],
        security_profile: Dict[str, str],
        extra_files: Optional[Dict[str, str]] = None,
    ) -> None:
        mdir = modes_root / mode_id
        mdir.mkdir(parents=True, exist_ok=True)

        files_map = {
            "README.md": f"# {name} Mode\n\n{description}\n",
            "core.md": f"# {name} Core Directives\n\n{core_guidelines}\n",
            "tools.md": f"# {name} Tools & SDKs\n\n{tools_content}\n",
            "quality-gate.md": f"# {name} Quality Gate\n\n" + "\n".join([f"- [ ] {g}" for g in quality_gates]) + "\n",
        }
        if extra_files:
            files_map.update(extra_files)

        for fname, content in files_map.items():
            with open(mdir / fname, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")

        catalog.append({
            "id": mode_id,
            "name": name,
            "category": category,
            "description": description,
            "version": "1.0.0",
            "dependencies": dependencies,
            "tags": tags,
            "directory": mode_id,
            "files": list(files_map.keys()),
            "quality_gates": quality_gates,
            "security_profile": security_profile,
        })

    # -------------------------------------------------------------
    # 2. DEVELOPMENT MODES
    # -------------------------------------------------------------
    add_mode(
        "frontend", "Frontend Development", "Development",
        "Modern frontend development focusing on reactive interfaces, accessibility, and high performance.",
        ["frontend", "ui", "react", "vue", "svelte", "css", "html"], [],
        "Focus on component architecture, state management, accessibility, and design tokens.",
        "React, Next.js, Vue, Vite, TailwindCSS, Vitest.",
        ["WCAG AA compliance", "Responsive viewport testing", "Component modularity"],
        {"xss_defense": "Sanitize all dynamic HTML"},
    )

    add_mode(
        "backend", "Backend Development", "Development",
        "Scalable server-side architecture, APIs, microservices, databases, and message queues.",
        ["backend", "api", "database", "node", "python", "golang", "microservices"], [],
        "Implement layered architecture (controller-service-repository), robust validation, connection pooling, and idempotent endpoints.",
        "Node.js, Express, FastAPI, Go, PostgreSQL, Redis, Docker.",
        ["All endpoints documented with OpenAPI", "Input validation on all routes", "Database migrations in place"],
        {"auth": "Secure session/JWT rotation", "secrets": "Environment variable isolation"},
    )

    add_mode(
        "fullstack", "Full-Stack Development", "Development",
        "Complete end-to-end full-stack development bridging client, server, and persistent storage.",
        ["fullstack", "web", "frontend", "backend", "database"], ["frontend", "backend"],
        "Integrate client-side experiences with performant backend services and relational databases.",
        "Next.js, FastAPI, Node.js, PostgreSQL, Docker, Playwright.",
        ["E2E integration test suite passes", "Unified error handling", "Secure data flow"],
        {"security": "End-to-end TLS and input validation"},
    )

    add_mode(
        "android", "Android Development", "Development",
        "Native Android app development following modern Android architecture and Jetpack Compose.",
        ["android", "kotlin", "jetpack", "mobile", "compose"], [],
        "Strict adherence to Material 3, Android lifecycle management, ViewModel, StateFlow, Room database, and coroutines.",
        "Kotlin, Android Studio, Gradle, Jetpack Compose, Room, Retrofit, JUnit.",
        ["Zero ANR (Application Not Responding) risks", "Proper lifecycle state handling", "Proguard/R8 enabled for release"],
        {"storage": "EncryptedSharedPreferences and Android Keystore"},
    )

    add_mode(
        "ios", "iOS Development", "Development",
        "Native iOS development adhering to Apple Human Interface Guidelines and SwiftUI.",
        ["ios", "swift", "swiftui", "apple", "mobile"], [],
        "Declarative SwiftUI, structured concurrency (async/await), SwiftData/CoreData, and Apple HIG compliance.",
        "Swift, Xcode, SwiftUI, SwiftData, XCTest, Instruments.",
        ["Apple HIG compliant UI", "No memory leaks in Instruments", "Strict accessibility voiceover labels"],
        {"storage": "iOS Keychain for sensitive credentials"},
    )

    add_mode(
        "crossplatform", "Cross-Platform App Development", "Development",
        "Multi-platform mobile and desktop development using Flutter and React Native.",
        ["crossplatform", "flutter", "reactnative", "dart", "mobile"], [],
        "Single codebase architecture with platform-specific native adapters and consistent rendering.",
        "Flutter, React Native, Dart, TypeScript, Expo.",
        ["Runs cleanly on iOS and Android", "Native feature bridging validated", "Consistent performance at 60fps"],
        {"permissions": "Explicit permission requests at runtime"},
    )

    add_mode(
        "desktop", "Desktop Application Development", "Development",
        "Cross-platform desktop application development for Windows, macOS, and Linux.",
        ["desktop", "electron", "tauri", "qt", "csharp", "rust"], [],
        "Resource-efficient desktop apps with native system integration, system tray, and auto-updates.",
        "Tauri, Electron, Rust, C#, .NET, Qt.",
        ["Installer creation verified", "Low idle memory footprint", "Proper OS integration"],
        {"sandbox": "Restricted file access permissions"},
    )

    add_mode(
        "windows-dev", "Windows Development", "Development",
        "Native Windows software engineering, WinUI, WPF, PowerShell scripting, and .NET.",
        ["windows", "csharp", "dotnet", "wpf", "winui", "powershell"], [],
        "Leverage modern .NET, async Windows APIs, PowerShell automation, and MSIX packaging. Safeguard system registry.",
        "C#, .NET 8/9, Visual Studio, PowerShell, Windows Terminal.",
        ["Safe registry and filesystem operations", "Clean uninstallation", "Signed executables"],
        {"privilege": "Require least privilege; no unauthorized UAC elevation"},
    )

    add_mode(
        "linux-dev", "Linux Development", "Development",
        "Linux systems programming, bash automation, systemd services, and container orchestration.",
        ["linux", "bash", "systemd", "c", "cplusplus", "posix"], [],
        "Adhere to POSIX standards, proper signal handling, file permissions, daemonization, and package management.",
        "Bash, GCC/Clang, systemd, Docker, Make, GDB.",
        ["Safe shell quoting in scripts", "Zero file descriptor leaks", "Idempotent service units"],
        {"security": "No execution as root unless strictly necessary"},
    )

    add_mode(
        "macos-dev", "macOS Development", "Development",
        "macOS native applications, AppKit, Swift, and Command Line Tools.",
        ["macos", "apple", "swift", "appkit", "darwin"], [],
        "Follow macOS Human Interface Guidelines, notarization, sandbox security, and universal binaries.",
        "Swift, Xcode, AppKit, Homebrew, lldb.",
        ["Hardened runtime enabled", "Notarization ready", "Apple Silicon and Intel support"],
        {"sandbox": "App sandbox enabled with explicit entitlements"},
    )

    add_mode(
        "game-dev", "Game Development", "Development",
        "Interactive game design, real-time loops, physics, rendering, and gameplay mechanics.",
        ["game", "godot", "unity", "unreal", "cplusplus", "csharp"], [],
        "Frame-rate independent loops, entity component systems (ECS), memory pooling, and spatial partitioning.",
        "Godot, Unity, Unreal Engine, C++, C#, Blender.",
        ["Consistent 60+ FPS performance", "Zero asset memory leaks", "Input remapping supported"],
        {"assets": "Clean asset licensing and copyright verification"},
    )

    add_mode(
        "software-engineering", "Software Engineering", "Development",
        "Rigorous software engineering, architecture, design patterns, SOLID principles, and clean code.",
        ["engineering", "architecture", "solid", "patterns", "uml", "srs"], [],
        "Requirements analysis, architectural diagrams, SOLID principles, clean architecture, and defensive programming.",
        "UML, Git, CI/CD, SonarQube, pytest/JUnit, Docker.",
        ["SRS / Architecture document created", "SOLID principles verified", "High test coverage on business logic"],
        {"review": "Peer code review standards enforced"},
    )

    add_mode(
        "computer-science", "Computer Science", "Development",
        "Fundamental computer science theory, algorithms, data structures, and computational complexity.",
        ["cs", "algorithms", "datastructures", "complexity", "theory"], [],
        "Algorithmic correctness, Big-O time and space optimization, formal invariants, and proof sketches.",
        "Python, C++, Graphviz, LeetCode style test harnesses.",
        ["Formal complexity analysis provided", "Boundary condition tests verified", "No memory/stack overflow"],
        {"verification": "Mathematical correctness of state machines and recursion"},
    )

    add_mode(
        "computer-engineering", "Computer Engineering", "Development",
        "Hardware-software interfaces, microcontrollers, embedded systems, and digital electronics.",
        ["ce", "hardware", "microcontroller", "embedded", "arm", "fpga"], [],
        "Timing diagrams, hardware registers, interrupt service routines, low power design, and peripheral buses.",
        "C, Assembly, ARM Cortex, Verilog, KiCad, PlatformIO.",
        ["Timing closure verified", "Race condition free interrupts", "Memory-mapped I/O verified"],
        {"safety": "Fail-safe hardware states on crash"},
    )

    add_mode(
        "devops", "DevOps & Infrastructure", "Development",
        "Infrastructure as Code, CI/CD pipelines, containerization, and automated deployments.",
        ["devops", "docker", "kubernetes", "terraform", "cicd", "gitops"], [],
        "Declarative infrastructure, immutable deployments, automated rollbacks, and secret management.",
        "Docker, Kubernetes, GitHub Actions, Terraform, Helm, Prometheus.",
        ["Linter and security scans in pipeline", "Zero plaintext secrets in git", "Reproducible builds"],
        {"access": "Principle of least privilege across cloud IAM"},
    )

    add_mode(
        "cloud-dev", "Cloud Development", "Development",
        "Cloud-native architecture, serverless, microservices, and distributed cloud services.",
        ["cloud", "aws", "gcp", "azure", "serverless", "lambda"], [],
        "High availability, horizontal autoscaling, fault tolerance, and cost optimization.",
        "AWS, GCP, Azure, Terraform, Serverless Framework, Cloudflare Workers.",
        ["Multi-region resilience planned", "Cloud cost estimated", "Disaster recovery plan documented"],
        {"iam": "Fine-grained IAM roles and VPC isolation"},
    )

    add_mode(
        "embedded", "Embedded Systems", "Development",
        "Real-time embedded firmware, RTOS, bare-metal programming, and sensor drivers.",
        ["embedded", "c", "firmware", "rtos", "stm32", "esp32"], [],
        "Deterministic latency, static memory allocation (no dynamic malloc in loops), and watchdog timers.",
        "C, FreeRTOS, ESP-IDF, STM32Cube, JTAG/SWD, Logic Analyzers.",
        ["Watchdog timer implemented", "Zero stack overflows", "Static memory bounds checked"],
        {"fault": "Safe state fallback upon brownout or crash"},
    )

    add_mode(
        "iot", "IoT Development", "Development",
        "Internet of Things connected devices, telemetry, MQTT, and edge gateways.",
        ["iot", "mqtt", "telemetry", "edge", "sensors", "arduino"], [],
        "Lightweight protocols (MQTT, CoAP), TLS encryption on all transmissions, and OTA firmware updates.",
        "MQTT, Mosquitto, Node-RED, InfluxDB, ESP32, Raspberry Pi.",
        ["Secure TLS communication", "OTA update verification with digital signatures", "Offline data buffering"],
        {"device_security": "Unique device credentials and secure boot"},
    )

    add_mode(
        "api-dev", "API Development", "Development",
        "Robust REST, GraphQL, and gRPC API engineering, schema design, and versioning.",
        ["api", "rest", "graphql", "grpc", "openapi", "swagger"], [],
        "Clear resource naming, schema contracts, backward compatibility, idempotency, and contract testing.",
        "OpenAPI, Postman, FastAPI, Apollo GraphQL, Protobuf, gRPC.",
        ["OpenAPI specification strictly matches code", "Contract tests pass", "Versioning strategy defined"],
        {"security": "Rate limiting and payload size limits enabled"},
    )

    # -------------------------------------------------------------
    # 3. DATA & AI MODES
    # -------------------------------------------------------------
    data_science_extra = {
        "python.md": "# Python Standards for Data Science\nPEP 8, type hints, vectorized operations using NumPy/Pandas.",
        "numpy.md": "# NumPy Guidelines\nUse vectorization; avoid pure Python loops over multidimensional arrays.",
        "pandas.md": "# Pandas Best Practices\nExplicit types, method chaining, avoid in-place mutations, handle NaN explicitly.",
        "statistics.md": "# Statistical Rigor\nVerify normality, choose parametric vs non-parametric tests, report p-values with effect sizes.",
        "reproducibility.md": "# Reproducibility Standards\nSet random seeds, pin dependency versions, export requirements.txt/environment.yml.",
    }
    add_mode(
        "data-science", "Data Science", "Data & AI",
        "Exploratory data analysis, statistical modeling, data cleaning, and reproducible pipelines.",
        ["data", "datascience", "python", "pandas", "numpy", "statistics", "eda"], [],
        "Complete data lifecycle: acquisition -> validation -> cleaning -> EDA -> modeling -> evaluation. Prevent data leakage.",
        "Python, Jupyter, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn.",
        ["Random seeds fixed for reproducibility", "No data leakage between train/test splits", "Missing values audited"],
        {"privacy": "Anonymize PII data before analysis"},
        extra_files=data_science_extra,
    )

    add_mode(
        "data-analysis", "Data Analysis", "Data & AI",
        "Business intelligence, metric analysis, cohort modeling, and actionable reporting.",
        ["analysis", "bi", "sql", "excel", "dashboards", "metrics"], [],
        "Focus on business questions, rigorous descriptive statistics, clear visualizations, and executive summaries.",
        "SQL, Python, PowerBI, Tableau, Excel, DuckDB.",
        ["Metrics verified against ground truth", "Visualizations clearly labeled with units", "Assumptions documented"],
        {"data_integrity": "Validate data sources for freshness and completeness"},
    )

    add_mode(
        "data-engineering", "Data Engineering", "Data & AI",
        "Data pipelines, ETL/ELT pipelines, warehousing, data lakes, and streaming architectures.",
        ["dataengineering", "etl", "spark", "airflow", "sql", "dbt", "kafka"], [],
        "Idempotent pipeline DAGs, data quality assertions, schema evolution, and partitioned storage.",
        "Apache Spark, Airflow, dbt, Snowflake, PostgreSQL, Kafka.",
        ["Pipelines are idempotent", "Data quality checks (Great Expectations / dbt tests)", "SLA monitoring in place"],
        {"compliance": "Data retention and GDPR right-to-be-forgotten compliance"},
    )

    add_mode(
        "machine-learning", "Machine Learning", "Data & AI",
        "Supervised and unsupervised learning, feature engineering, model evaluation, and validation.",
        ["ml", "machinelearning", "scikit", "xgboost", "classification", "regression"], ["data-science"],
        "Strict train/validation/test isolation, appropriate metrics (F1, AUC-ROC, RMSE), and cross-validation.",
        "Scikit-learn, XGBoost, LightGBM, Optuna, MLflow.",
        ["Cross-validation executed", "Baseline comparison documented", "Feature importance analyzed"],
        {"fairness": "Evaluate model bias across demographic groups"},
    )

    add_mode(
        "deep-learning", "Deep Learning", "Data & AI",
        "Deep neural networks, PyTorch, backpropagation, CNNs, RNNs, and custom architectures.",
        ["deeplearning", "pytorch", "tensorflow", "neuralnetworks", "cuda"], ["machine-learning"],
        "Gradient checking, learning rate schedules, weight decay regularization, and GPU memory optimization.",
        "PyTorch, TensorBoard, Hugging Face, CUDA, Weights & Biases.",
        ["Loss curves inspected for overfitting", "Checkpoints saved with optimizer state", "Evaluation on unseen test set"],
        {"reproducibility": "Deterministic CUDA algorithms enabled where possible"},
    )

    add_mode(
        "artificial-intelligence", "Artificial Intelligence", "Data & AI",
        "Broad AI systems, search algorithms, heuristic planning, expert systems, and agents.",
        ["ai", "agents", "search", "heuristics", "reasoning"], [],
        "Agentic reasoning loops, graph search (A*, Minimax), knowledge representation, and constraint satisfaction.",
        "Python, Prolog, NetworkX, AI agent toolkits.",
        ["Heuristics proved admissible", "State space complexity analyzed", "Safety guardrails in agent execution"],
        {"ethics": "Responsible AI transparency and human oversight"},
    )

    add_mode(
        "generative-ai", "Generative AI", "Data & AI",
        "LLMs, prompt engineering, RAG (Retrieval-Augmented Generation), fine-tuning, and diffusion models.",
        ["genai", "llm", "rag", "langchain", "embeddings", "vector"], [],
        "Structured output generation, hallucination mitigation, vector search evaluation, and prompt safety.",
        "LangChain, LlamaIndex, ChromaDB, Hugging Face, Gemini API, PyTorch.",
        ["RAG retrieval evaluated for relevancy", "Hallucination guardrails active", "Cost and token budgets monitored"],
        {"safety": "Filter toxic inputs and sanitize model responses"},
    )

    add_mode(
        "nlp", "Natural Language Processing (NLP)", "Data & AI",
        "Text classification, sentiment analysis, NER, tokenization, and transformer models.",
        ["nlp", "transformers", "spacy", "text", "bert", "tokenization"], ["deep-learning"],
        "Subword tokenization, attention mechanisms, BLEU/ROUGE metrics, and language representation.",
        "spaCy, NLTK, Hugging Face Transformers, PyTorch.",
        ["Vocabulary coverage checked", "Out-of-vocabulary handling in place", "Latency benchmarks recorded"],
        {"privacy": "Filter PII from text corpora"},
    )

    add_mode(
        "computer-vision", "Computer Vision", "Data & AI",
        "Image classification, object detection, segmentation, and OpenCV pipelines.",
        ["computervision", "cv", "opencv", "yolo", "segmentation", "images"], ["deep-learning"],
        "Data augmentation, bounding box coordinate normalization, IoU metrics, and color space handling.",
        "OpenCV, torchvision, YOLO, Albumentations, PyTorch.",
        ["Mean Average Precision (mAP) evaluated", "Inference FPS benchmarked", "Edge case illumination tested"],
        {"privacy": "Blur faces and license plates where required by privacy laws"},
    )

    add_mode(
        "mlops", "MLOps", "Data & AI",
        "Machine learning lifecycle automation, model registries, monitoring, and continuous training.",
        ["mlops", "mlflow", "kserve", "pipelines", "monitoring", "drift"], ["machine-learning", "devops"],
        "Automated model retraining, feature stores, data drift detection, and canary deployments.",
        "MLflow, Kubeflow, Feast, Evidentially, Docker, Prometheus.",
        ["Data and concept drift monitors active", "Model version rollback tested", "Inference latency alerts set"],
        {"governance": "Model card and lineage tracked in registry"},
    )

    # -------------------------------------------------------------
    # 4. SECURITY MODES
    # -------------------------------------------------------------
    add_mode(
        "cybersecurity", "Cybersecurity", "Cybersecurity",
        "Defensive security engineering, threat modeling, hardening, cryptography, and compliance.",
        ["security", "cybersecurity", "threatmodeling", "appsec", "hardening"], [],
        "Defensive in-depth, STRIDE threat modeling, least privilege, zero trust, and secure system baselines.",
        "Wireshark, Nmap, OpenVAS, OSSEC, OWASP ZAP, Cryptography libs.",
        ["Threat model documented", "Security headers verified", "Vulnerability scan resolved"],
        {"defensive_only": "All actions must be defensive and compliant with security policies"},
    )

    add_mode(
        "ethical-hacking", "Ethical Hacking", "Cybersecurity",
        "Authorized offensive security testing, penetration testing methodologies, and remediation.",
        ["ethicalhacking", "pentest", "redteam", "recon", "authorized"], [],
        "STRICT AUTHORIZATION MANDATORY. Verify scope, rules of engagement, and legal permission. No destructive actions.",
        "Nmap, Burp Suite, Metasploit (lab only), Gobuster, Nikto, OWASP Top 10.",
        ["Explicit written authorization verified", "Target in scope verified", "Remediation guide provided"],
        {"authorization": "Zero activity outside approved scope; non-destructive testing only"},
    )

    add_mode(
        "penetration-testing", "Penetration Testing", "Cybersecurity",
        "Comprehensive vulnerability assessment, exploitation validation in authorized test labs, and reporting.",
        ["pentest", "vulnerability", "audit", "securityreport"], ["ethical-hacking"],
        "Follow PTES (Penetration Testing Execution Standard). Document proof-of-concept steps and CVSS scores.",
        "Burp Suite, OWASP ZAP, SQLmap (lab only), Nessus.",
        ["CVSS v3.1 scoring applied", "Executive summary included", "Reproducible proof of concepts documented"],
        {"safety": "Never run intrusive tests on live production systems without permission"},
    )

    add_mode(
        "digital-forensics", "Digital Forensics", "Cybersecurity",
        "Incident investigation, artifact extraction, memory analysis, and chain of custody.",
        ["forensics", "incidentresponse", "dfir", "volatility", "autopsy"], [],
        "Maintain chain of custody, write-block original media, compute MD5/SHA256 hashes, and document timeline.",
        "Autopsy, Volatility, FTK Imager, Sleuth Kit, Wireshark.",
        ["Cryptographic hashes verified", "Timeline reconstructed", "Chain of custody documented"],
        {"evidence": "Preserve evidentiary integrity without modifying source images"},
    )

    add_mode(
        "network-security", "Network Security", "Cybersecurity",
        "Firewalls, intrusion detection, packet analysis, VPNs, and network segmentation.",
        ["networksecurity", "firewall", "snort", "suricata", "vpn", "ids"], ["cybersecurity"],
        "Segment networks via VLANs/subnets, configure IDS/IPS rules, inspect TLS traffic, and enforce 802.1X.",
        "Wireshark, Suricata, Snort, iptables, pfSense, OpenVPN.",
        ["Firewall ingress/egress rules audited", "IDS alerts baseline established", "No cleartext protocols in transit"],
        {"protection": "Block unauthorized lateral movement"},
    )

    add_mode(
        "app-security", "Application Security (AppSec)", "Cybersecurity",
        "Secure code reviews, SAST, DAST, dependency audits, and OWASP mitigation.",
        ["appsec", "sast", "dast", "owasp", "semgrep", "codeql"], ["cybersecurity"],
        "Audit code against OWASP Top 10, automated SAST scans, dependency vulnerability management (Snyk, Dependabot).",
        "Semgrep, CodeQL, OWASP ZAP, Trivy, npm audit, pip-audit.",
        ["Zero Critical/High CVEs in dependencies", "SAST clean of injection vulnerabilities", "CSRF/CORS audited"],
        {"prevention": "Remediate root cause, not merely symptoms"},
    )

    add_mode(
        "cloud-security", "Cloud Security", "Cybersecurity",
        "Cloud security posture management, IAM hardening, KMS encryption, and audit logging.",
        ["cloudsecurity", "iam", "kms", "aws", "gcp", "cisbenchmarks"], ["cybersecurity", "cloud-dev"],
        "Follow CIS Benchmarks, enforce MFA on root accounts, encrypt data at rest with KMS, enable CloudTrail.",
        "Prowler, ScoutSuite, AWS GuardDuty, Terraform Compliance.",
        ["CIS Benchmark scan passed", "No public S3 buckets with sensitive data", "Audit logs immutable"],
        {"compliance": "Enforce principle of least privilege on IAM roles"},
    )

    add_mode(
        "secure-software-dev", "Secure Software Development", "Cybersecurity",
        "Secure Software Development Lifecycle (SSDL), threat modeling in design, and secure coding standards.",
        ["ssdl", "devsecops", "threatmodel", "securecoding"], ["software-engineering", "cybersecurity"],
        "Integrate security checkpoints in each phase: design threat model, implementation SAST, CI/CD DAST, deployment review.",
        "OWASP SAMM, Semgrep, SonarQube, GitGuardian.",
        ["Threat model signoff before implementation", "Secret scanning active in pre-commit", "Security gate passed"],
        {"policy": "Fail builds on high security vulnerabilities"},
    )

    # -------------------------------------------------------------
    # 5. COMPUTER & ENGINEERING MODES
    # -------------------------------------------------------------
    add_mode(
        "computer-networks", "Computer Networks", "Computer & Engineering",
        "OSI & TCP/IP stack, routing protocols, subnetting, VLANs, and Packet Tracer simulation.",
        ["networking", "cisco", "tcpip", "osi", "routing", "subnetting"], [],
        "Subnet calculation accuracy, protocol packet breakdown (TCP 3-way handshake, DNS, DHCP, ARP), and routing tables.",
        "Wireshark, Cisco Packet Tracer, GNS3, ping/traceroute.",
        ["Subnet calculations verified without overlap", "Packet flow traced across layers", "Routing tables converged"],
        {"integrity": "Validate network topologies against broadcast storms"},
    )

    add_mode(
        "network-engineering", "Network Engineering", "Computer & Engineering",
        "Enterprise network design, BGP, OSPF, MPLS, SD-WAN, and high-availability topologies.",
        ["networkeng", "bgp", "ospf", "cisco", "juniper", "mpls"], ["computer-networks"],
        "Dual-homed redundancy, link aggregation (LACP), spanning tree protocol tuning, and QoS prioritization.",
        "Cisco IOS, Junos, FRRouting, Ansible networking.",
        ["Failover test verified under simulated link drop", "QoS policies configured for voice/video", "BGP peering secured"],
        {"security": "Control-plane policing (CoPP) implemented"},
    )

    add_mode(
        "digital-logic", "Digital Logic Design", "Computer & Engineering",
        "Boolean algebra, combinational circuits, sequential circuits, FSMs, and HDL simulation.",
        ["logic", "digitallogic", "verilog", "kmap", "circuits", "fsm"], [],
        "Karnaugh map minimization, gate delay analysis, setup and hold times, Mealy/Moore finite state machines.",
        "Logisim, Digital, ModelSim, Verilog/VHDL, Icarus Verilog.",
        ["Truth table matches Boolean equations", "No hazard glitches in combinational logic", "FSM states exhaustive and deterministic"],
        {"timing": "Setup and hold times satisfied in sequential logic"},
    )

    add_mode(
        "computer-architecture", "Computer Architecture", "Computer & Engineering",
        "CPU datapath, pipelining, cache hierarchies, branch prediction, and instruction set architectures.",
        ["architecture", "riscv", "mips", "pipelining", "cache", "assembly"], ["computer-engineering"],
        "5-stage RISC pipeline, hazards (data, control, structural), cache hit/miss penalties, and memory alignment.",
        "RISC-V simulator, MARS, Gem5, C, Assembly.",
        ["Hazard detection and forwarding verified", "Cache memory mapping calculated", "Instruction cycle timings verified"],
        {"correctness": "Assembly programs yield identical architectural register state"},
    )

    add_mode(
        "operating-systems", "Operating Systems", "Computer & Engineering",
        "Process scheduling, virtual memory, concurrency, file systems, and system calls.",
        ["os", "processes", "threads", "paging", "mutex", "deadlock"], ["computer-science"],
        "Thread synchronization (mutex, semaphores), deadlock avoidance (Banker's algorithm), page replacement (LRU).",
        "C, POSIX pthreads, xv6, Linux kernel, QEMU.",
        ["Zero deadlocks or race conditions (ThreadSanitizer clean)", "Paging tables correctly aligned", "System calls safe against invalid user pointers"],
        {"isolation": "Strict user-space and kernel-space memory separation"},
    )

    add_mode(
        "distributed-systems", "Distributed Systems", "Computer & Engineering",
        "Consensus algorithms, CAP theorem, distributed storage, RPC, and fault tolerance.",
        ["distributed", "raft", "paxos", "grpc", "cap", "consensus"], ["backend"],
        "Consensus (Raft/Paxos), vector clocks, idempotency, split-brain protection, and eventual consistency.",
        "Go, gRPC, etcd, Consul, Redis Sentinel, Docker.",
        ["Network partition resilience tested", "Leader election determinism verified", "Idempotent message handling"],
        {"fault_tolerance": "System survives minority node failures"},
    )

    add_mode(
        "database-engineering", "Database Engineering", "Computer & Engineering",
        "Storage engines, B-trees, WAL logs, query optimization, ACID transactions, and indexing.",
        ["database", "sql", "indexing", "btree", "acid", "queryoptimization"], [],
        "Query execution plans (EXPLAIN ANALYZE), index selection, isolation levels, replication, and sharding.",
        "PostgreSQL, MySQL, SQLite, Redis, pgAdmin, pt-query-digest.",
        ["All queries use indexes (no sequential scans on large tables)", "Transaction isolation verified", "Normalization checked"],
        {"durability": "WAL and backup recovery verified"},
    )

    add_mode(
        "systems-programming", "Systems Programming", "Computer & Engineering",
        "Low-level programming, manual memory management, zero-cost abstractions, and C/Rust.",
        ["systems", "c", "rust", "lowlevel", "memory", "pointers"], [],
        "Memory safety, pointer arithmetic bounds, cache locality, RAII, and error propagation.",
        "Rust, C, GCC/Clang, Valgrind, AddressSanitizer, GDB.",
        ["Valgrind / ASan report zero memory leaks or buffer overflows", "Zero undefined behavior", "Clean error handling"],
        {"safety": "Rust unsafe blocks strictly audited; C input bounds checked"},
    )

    add_mode(
        "hardware-software-integration", "Hardware/Software Integration", "Computer & Engineering",
        "Device drivers, communication protocols (I2C, SPI, UART, CAN), and board bring-up.",
        ["integration", "drivers", "i2c", "spi", "uart", "canbus"], ["embedded", "computer-engineering"],
        "Protocol timing analysis, bus arbitration, register access abstraction, and interrupt handling.",
        "Oscilloscope, Logic Analyzer, Saleae, C, Python.",
        ["Bus clock rates and timing verified", "Error handling on lost ACK / timeout", "Driver interface modular"],
        {"electrical": "Check voltage levels (3.3V vs 5V) before connection"},
    )

    # -------------------------------------------------------------
    # 6. ACADEMIC & STUDY MODES
    # -------------------------------------------------------------
    add_mode(
        "mathematics", "Mathematics", "Academic & Study",
        "Calculus, linear algebra, discrete math, differential equations, and formal proofs.",
        ["math", "calculus", "linearalgebra", "probability", "discrete"], [],
        "Show step-by-step rigorous derivations, state theorems and conditions clearly, and provide geometric intuition.",
        "SymPy, NumPy, SciPy, LaTeX, Wolfram Alpha format.",
        ["All intermediate derivation steps shown", "Domain and boundary conditions checked", "Formulas formatted in LaTeX"],
        {"accuracy": "Verify solutions by substitution"},
    )

    add_mode(
        "physics", "Physics", "Academic & Study",
        "Classical mechanics, electromagnetism, thermodynamics, quantum physics, and dimensional analysis.",
        ["physics", "mechanics", "electromagnetism", "thermodynamics", "units"], [],
        "Always perform dimensional analysis, state reference frames, define coordinate systems, and verify limiting cases.",
        "Python, VPython, SciPy, Matplotlib.",
        ["Units and dimensions match on both sides", "Limiting cases (e.g. v -> 0, t -> infinity) behave logically", "Free-body diagrams described"],
        {"precision": "Correct significant figures maintained"},
    )

    add_mode(
        "chemistry", "Chemistry", "Academic & Study",
        "General, organic, physical chemistry, reaction stoichiometry, and laboratory safety.",
        ["chemistry", "organic", "reactions", "stoichiometry", "equations"], [],
        "Balance chemical equations, check stoichiometry, detail reaction mechanisms (curved arrows), and state laboratory safety hazards.",
        "RDKit, ChemDraw format, MolView.",
        ["Chemical equations balanced by mass and charge", "Safety hazards (MSDS) listed for all reagents", "Limiting reagents calculated"],
        {"safety": "Explicit laboratory PPE and hazard warnings"},
    )

    add_mode(
        "statistics", "Statistics", "Academic & Study",
        "Inferential statistics, probability distributions, hypothesis testing, and regression analysis.",
        ["statistics", "probability", "hypothesis", "pvalue", "anova"], [],
        "Check distributional assumptions, formulate null/alternative hypotheses, report confidence intervals and effect sizes.",
        "R, Python, statsmodels, SciPy.",
        ["Assumptions checked (homoscedasticity, normality)", "Confidence intervals reported with point estimates", "No p-hacking"],
        {"interpretation": "Distinguish statistical significance from practical significance"},
    )

    add_mode(
        "computer-science-study", "Computer Science Study", "Academic & Study",
        "Academic coursework assistance, textbook concept explanation, and educational tutorials.",
        ["study", "tutoring", "concepts", "explanations", "homeworkhelp"], ["computer-science"],
        "Guide the student through conceptual understanding with progressive hints, intuitive analogies, and interactive examples.",
        "Python, Diagrams, Markdown.",
        ["Step-by-step conceptual walkthrough provided", "Analogies ground abstract concepts", "Encourages independent problem-solving"],
        {"academic_integrity": "Provide pedagogical explanations rather than blindly executing exam submissions"},
    )

    add_mode(
        "engineering-study", "Engineering Study", "Academic & Study",
        "Engineering fundamentals, design principles, calculations, and coursework problem solving.",
        ["engineeringstudy", "circuits", "statics", "dynamics", "materials"], [],
        "Identify given variables, state governing laws, show unit conversions, and verify final numerical answers.",
        "Python, MATLAB format, engineering spreadsheets.",
        ["Governing equations stated explicitly", "All conversion factors shown", "Order-of-magnitude sanity check passed"],
        {"standards": "Adhere to IEEE, ASME, ISO engineering conventions"},
    )

    add_mode(
        "exam-prep", "Exam Preparation", "Academic & Study",
        "Targeted study plans, practice questions, MCQs, mock exams, and weak-area diagnosis.",
        ["examprep", "mcq", "practice", "revision", "mocktest"], [],
        "Generate practice problems with detailed rationales for correct and incorrect options. Time management strategies.",
        "Quiz engines, Flashcard format, Markdown.",
        ["Explanations provided for both right and wrong answers", "Key formulas summarized", "Progressive difficulty scaling"],
        {"learning": "Reinforce memory retention and problem-solving speed"},
    )

    add_mode(
        "project-research", "Assignment & Project Research", "Academic & Study",
        "Structured academic project research, literature search, methodology design, and citation management.",
        ["projectresearch", "academic", "methodology", "citations", "references"], [],
        "Define research questions, formulate methodologies, compare existing literature, and format citations (IEEE, APA, Harvard).",
        "Zotero format, BibTeX, Google Scholar search strategies.",
        ["Research questions clearly articulated", "Credible peer-reviewed sources cited", "Plagiarism-free paraphrasing"],
        {"academic_honesty": "Full citation tracking without ghost references"},
    )

    add_mode(
        "general-research", "General Research", "Research",
        "Fact-based investigative research, multi-source synthesis, authoritative validation, and source citations.",
        ["research", "investigation", "citations", "synthesis", "analysis"], [],
        "Identify primary authoritative sources, cross-reference claims across multiple sources, state dates, and avoid fabricated facts.",
        "Search tools, Markdown reports, Citation generators.",
        ["Multiple independent sources cross-verified", "Exact dates and source attribution provided", "No hallucinated citations"],
        {"truthfulness": "Distinguish established facts from disputed opinions"},
    )

    # -------------------------------------------------------------
    # 7. LANGUAGES & WRITING MODES
    # -------------------------------------------------------------
    add_mode(
        "english", "English Language & Writing", "Languages & Writing",
        "Grammar, vocabulary, rhetoric, stylistic editing, and fluency improvement.",
        ["english", "writing", "grammar", "vocabulary", "editing"], [],
        "Tone calibration (formal, conversational, persuasive), active voice emphasis, conciseness, and idiomatic precision.",
        "Grammarly guidelines, Chicago Manual of Style.",
        ["Zero grammatical or punctuation errors", "Varied sentence structure", "Tone matches target audience"],
        {"clarity": "Eliminate redundant filler words"},
    )

    add_mode(
        "urdu", "Urdu Language (اردو)", "Languages & Writing",
        "Urdu linguistics, grammar (قواعد), translation, poetry analysis, and formal composition in Nastaliq.",
        ["urdu", "اردو", "language", "translation", "literature"], [],
        "Correct orthography (املاء), syntax (نحو), vocabulary, authentic idioms (محاورات), and elegant Urdu expression.",
        "Urdu Unicode, Rekhta references, Muqtadra standards.",
        ["Correct Urdu spelling and syntax", "Context-appropriate vocabulary", "Accurate bidirectional translation"],
        {"cultural_respect": "Preserve literary and cultural nuances of Urdu"},
    )

    add_mode(
        "arabic", "Arabic Language (العربية)", "Languages & Writing",
        "Classical and Modern Standard Arabic, grammar (النحو والصرف), vocabulary, and translation.",
        ["arabic", "العربية", "nahw", "sarf", "translation"], [],
        "Adherence to Nahw (grammar), Sarf (morphology), Balaghah (rhetoric), and accurate tashkeel (diacritics) where needed.",
        "Arabic lexicons (Lisan al-Arab, Hans Wehr), Unicode.",
        ["Grammatical agreement (gender, number, case) verified", "Accurate root-derived vocabulary", "Fluent Arabic phrasing"],
        {"accuracy": "Preserve classical grammatical precision"},
    )

    add_mode(
        "technical-writing", "Technical Writing", "Languages & Writing",
        "Developer documentation, API guides, user manuals, release notes, and architecture specs.",
        ["technicalwriting", "documentation", "api-docs", "manuals", "guides"], [],
        "Clarity, conciseness, actionable steps, code examples with expected outputs, and progressive disclosure.",
        "Markdown, Mermaid.js, Swagger/OpenAPI, Docusaurus.",
        ["All code examples verified runnable", "Prerequisites stated before instructions", "Glossary for technical jargon"],
        {"security": "Never include real API keys or passwords in documentation examples"},
    )

    add_mode(
        "academic-writing", "Academic Writing", "Languages & Writing",
        "Theses, journal papers, literature reviews, abstracts, and peer-reviewed publishing standards.",
        ["academicwriting", "thesis", "paper", "abstract", "peerreview"], [],
        "Formal objective tone, logical paragraph progression, strong thesis statements, and rigorous citation integration.",
        "LaTeX, BibTeX, APA/IEEE style guides.",
        ["Clear thesis statement and logical flow", "Impersonal academic register maintained", "All claims backed by citations"],
        {"integrity": "Zero plagiarism; proper synthesis of references"},
    )

    # -------------------------------------------------------------
    # 8. GENERAL & KNOWLEDGE MODES (including ISLAMIC KNOWLEDGE MODE)
    # -------------------------------------------------------------
    islamic_extra = {
        "primary-sources.md": """# Strict Islamic Textual Source Control
The ONLY primary textual authorities permitted for religious claims:
1. The Holy Quran
2. Sahih al-Bukhari (صحيح البخاري)
3. Sahih Muslim (صحيح مسلم)
4. Sunan Abu Dawud (سنن أبي داود)
5. Jami' al-Tirmidhi (جامع الترمذي)
6. Sunan al-Nasa'i (سنن النسائي)
7. Sunan Ibn Majah (سنن ابن ماجه)

### Strict Citation Rules:
- **Quran**: Always cite the Surah name and Verse number (e.g., *Surah Al-Baqarah 2:255*).
- **Hadith**: Always state the specific collection, book/chapter, and hadith number (e.g., *Sahih al-Bukhari, Hadith 1*).
- **Zero Hallucination**: Never invent, guess, or rephrase a text as a quote. If a hadith is not verified in these 6 books, declare it unverified.
- Clearly distinguish between: Quranic Text, Hadith Text, Translation, and Scholarly Interpretation.
""",
        "methodology.md": """# Islamic Scholarship Methodology
- Context of revelation (Asbab al-Nuzul) when relevant.
- Scholarly consensus (Ijma) and established linguistic meanings.
- Neutral presentation of differing classical madhab viewpoints where consensus does not exist.
""",
    }
    add_mode(
        "islamic-knowledge", "Islamic Knowledge", "General",
        "Authentic Islamic knowledge with strict primary source control: Quran and the Six Canonical Hadith Collections only.",
        ["islamic", "quran", "hadith", "bukhari", "muslim", "sources", "citations"], [],
        "STRICT SOURCE CONTROL. Cite only Quran and the 6 canonical collections (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah). Provide exact Surah:Ayah and Hadith numbers. Never hallucinate.",
        "Quranic corpus, Hadith indexing, Classical Arabic lexicons.",
        ["Surah and Ayah number verified for all Quranic verses", "Hadith collection and number verified for all narrations", "Zero unsourced religious claims"],
        {"truthfulness": "Zero fabrication policy; state lack of verified source rather than speculating"},
        extra_files=islamic_extra,
    )

    add_mode(
        "general-ai", "General AI Assistant", "General",
        "Balanced, helpful, adaptive pair programmer and general problem solver.",
        ["general", "assistant", "helper", "default"], [],
        "Adapt to the user's explicit goals, clarify ambiguities when needed, provide clean modular solutions.",
        "Standard multi-language toolsets.",
        ["Code solutions tested for correctness", "Clear concise explanations", "Clean formatting"],
        {"safety": "Adhere to standard system safety boundaries"},
    )

    add_mode(
        "documentation", "Documentation Mode", "General",
        "Comprehensive documentation generator for codebases, architectures, and user guides.",
        ["docs", "documentation", "readme", "architecture", "diagrams"], [],
        "Generate complete README, architectural overviews, API contracts, Mermaid diagrams, and setup instructions.",
        "Markdown, Mermaid.js, MkDocs, typedoc/jsdoc.",
        ["README covers setup, usage, and architecture", "Mermaid diagrams render without errors", "No broken links"],
        {"privacy": "Sanitize all configuration examples of sensitive credentials"},
    )

    add_mode(
        "technical-research", "Technical Research", "General",
        "In-depth research on emerging technologies, libraries, benchmarks, and architectural tradeoffs.",
        ["techresearch", "benchmarks", "evaluations", "tradeoffs"], [],
        "Benchmark comparison, quantitative metrics, licensing review, and migration difficulty analysis.",
        "Search tools, benchmark suites, Markdown comparison tables.",
        ["Pros and cons matrix provided", "Performance and memory benchmarks cited", "License compatibility confirmed"],
        {"accuracy": "Verify against active documentation and latest releases"},
    )

    add_mode(
        "literature-review", "Literature Review", "General",
        "Systematic review of state-of-the-art research papers, patents, and technical literature.",
        ["literature", "review", "papers", "academic", "stateoftheart"], [],
        "Define taxonomy, summarize key methodologies, highlight gaps in existing work, and synthesize findings.",
        "BibTeX, Google Scholar search syntax, Markdown.",
        ["Taxonomy clearly categorizes surveyed works", "Critical analysis of methodology limitations", "Comprehensive references"],
        {"synthesis": "Synthesize themes rather than listing unconnected summaries"},
    )

    add_mode(
        "project-planning", "Project Planning & Roadmapping", "General",
        "WBS, milestone definition, risk assessment, sprint planning, and task breakdown.",
        ["planning", "roadmap", "milestones", "wbs", "risks", "scrum"], [],
        "Break project into phases: MVP, Phase 1, Phase 2. Estimate complexity, identify blockers and dependencies.",
        "Gantt format, Markdown task lists, Risk matrices.",
        ["Dependencies between tasks clearly mapped", "Risk mitigation strategies defined", "Definition of Done established"],
        {"feasibility": "Realistic scope management avoiding feature bloat"},
    )

    add_mode(
        "requirements-engineering", "Requirements Engineering", "General",
        "Functional & non-functional requirements elicitation, user stories, and acceptance criteria.",
        ["requirements", "userstories", "gherkin", "acceptancecriteria"], [],
        "Elicit functional requirements (FRs), non-functional requirements (NFRs: performance, security, scale), and Gherkin scenarios.",
        "User Story format, Gherkin / Cucumber format, Markdown.",
        ["All requirements have testable acceptance criteria", "NFR metrics are quantified (e.g. latency < 200ms)", "Edge cases captured"],
        {"traceability": "Unique IDs assigned to requirements for traceability"},
    )

    add_mode(
        "srs-development", "SRS Development", "General",
        "Software Requirements Specification (IEEE 830 / ISO/IEC/IEEE 29148 standard compliant).",
        ["srs", "spec", "ieee830", "software-spec", "formal"], ["requirements-engineering"],
        "Formal SRS document structure: Scope, Overall Description, System Features, External Interfaces, NFRs, and Verification Matrix.",
        "IEEE 830 format, Markdown, UML diagrams.",
        ["IEEE 830 structure followed", "System context diagram included", "Verification method specified for each requirement"],
        {"completeness": "Zero ambiguous requirement statements"},
    )

    add_mode(
        "general-work", "General Engineering Work", "General",
        "General-purpose engineering execution, refactoring, maintenance, and bug fixing.",
        ["work", "general", "refactoring", "maintenance"], [],
        "Maintain backwards compatibility, write regression tests for all bug fixes, preserve documentation integrity.",
        "Standard development tools.",
        ["Existing test suite passes", "Code conforms to project style guide", "Changelog updated"],
        {"safety": "Never delete or overwrite working code without backup"},
    )

    # Save the master index modes.json
    index_file = modes_root / "modes.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump({"version": "1.0.0", "modes": catalog}, f, indent=2)

    print(f"Generated {len(catalog)} modes in {modes_root}")


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent.parent / "modes"
    generate_library(target)
