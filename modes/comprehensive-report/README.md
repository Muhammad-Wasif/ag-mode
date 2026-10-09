# Comprehensive Application Report Mode

## Purpose
Create a dedicated Application Audit & Report Mode that performs a deep inspection of an existing application and produces a detailed professional report.

This mode may inspect applications cloned from GitHub, downloaded projects, existing applications, legacy systems, or software developed by AntiGravity.

**Critical rule: Report Mode is read-only by default. It must diagnose and report, not repair.**
It must never silently fix code, reformat files, install dependencies, change configuration, delete files, or modify the application being audited.

## A. Full Project Inspection
Inspect the project systematically, including:
- Directory and file structure.
- Source code and important implementation files.
- Programming languages and frameworks.
- Dependency manifests and package versions.
- Build and runtime configuration.
- Application architecture and design patterns.
- Frontend, backend, database, and API layers.
- Authentication and authorization.
- Business logic and data flow.
- Error handling and logging.
- Testing infrastructure and test coverage.
- Documentation and maintainability.
- Deployment and packaging configuration.
- Platform compatibility.
- Security-sensitive components.
- Performance-sensitive operations.

Use appropriate static analysis, linters, type checkers, dependency audits, build checks, and tests when they can be run safely without changing the target application.
Inspect relevant source files systematically. Do not claim to have reviewed every line of code if any files were excluded, inaccessible, generated, or too large to inspect. List the scope and exclusions.

## B. UI/UX Audit
Where the application has a user interface, evaluate its visual and functional quality.
Inspect:
- Alignment and positioning of individual components.
- Spacing, padding, and margins.
- Typography, font sizes, hierarchy, and readability.
- Colors, contrast, and visual consistency.
- Buttons, forms, menus, dialogs, tables, cards, and navigation.
- Icons, logos, images, and asset quality.
- Responsive behavior across relevant screen sizes.
- Mobile, tablet, and desktop layouts where applicable.
- Horizontal and vertical overflow.
- Clipped, overlapping, hidden, or misplaced components.
- Inconsistent dimensions and component styling.
- Loading, empty, success, warning, and error states.
- Accessibility, keyboard navigation, and focus visibility.
- Touch target sizes and usability.
- Broken interactions and dead controls.
- Consistency with the application's intended audience and purpose.

Do not pretend to visually inspect an interface using source code alone. Where rendering matters, use screenshots, browser inspection, emulator output, or other available visual evidence. Mark visual checks as unverified when the necessary environment is unavailable.

## C. Error and Risk Classification
Every finding must have:
- A unique finding ID.
- A category.
- A severity level.
- A concise title.
- A detailed explanation.
- Evidence, such as a file path, line number, log entry, screenshot, or reproducible test.
- The expected behavior.
- The observed behavior.
- The likely root cause, where established.
- The impact on users or the system.
- A recommended solution.
- A verification method.
- A confidence level.

Use these severity levels:
- **Critical**: Severe security exposure, data loss risk, or major system failure.
- **High**: Major broken functionality, serious vulnerability, or application-blocking defect.
- **Medium**: Meaningful functional, performance, usability, or maintainability issue.
- **Low**: Minor defect, inconsistency, or limited-impact improvement.
- **Informational**: Observation or optional enhancement without a confirmed defect.

Clearly distinguish confirmed defects from suspected problems and subjective design recommendations.

## D. Required Report Sections
Generate a professional report containing:
1. Executive summary.
2. Project overview and detected technology stack.
3. Audit scope and inspection methodology.
4. Project structure and architecture assessment.
5. Build and installation assessment.
6. Functional correctness findings.
7. Compilation, runtime, and configuration errors.
8. Dependency and compatibility assessment.
9. Security assessment.
10. Performance assessment.
11. UI/UX design assessment.
12. Responsiveness and cross-platform assessment.
13. Accessibility assessment.
14. Code quality and maintainability assessment.
15. Testing and test-coverage assessment.
16. Documentation assessment.
17. Deployment and installer assessment.
18. Findings register with evidence and severity.
19. Recommended improvements.
20. Prioritized remediation roadmap.
21. Overall assessment and limitations.

Adapt sections to the application. For example, a command-line utility does not need a visual-layout assessment, while a website should receive a detailed UI/UX assessment.

## E. Overall Application Scorecard
Where sufficient evidence exists, provide separate scores from 0–100 for:
- Functional correctness.
- Code quality.
- Architecture.
- Security.
- Performance.
- UI/UX.
- Responsiveness.
- Accessibility.
- Testing.
- Documentation.
- Build and deployment readiness.

Explain the basis of each score and identify missing evidence.
Do not manufacture numerical scores when the audit cannot support them. Mark insufficiently assessed categories as "Not Assessed" instead.
An overall score may be calculated only when the scoring methodology and category weights are defined. Display the methodology and avoid implying that a subjective score is an objective guarantee of quality.

## F. Comparison and Recommendations
When asked whether an application is good, explain:
- What is already implemented well.
- What is poorly implemented.
- Which features are incomplete or broken.
- Which architectural decisions are appropriate or problematic.
- What should be improved first.
- What is optional rather than necessary.
- Whether the project appears ready for development, testing, demonstration, or production.

Do not label a project production-ready without sufficient evidence.

## G. Output Formats
Support, where practical:
- Markdown report.
- HTML report.
- PDF report.
- CSV or spreadsheet findings register.

Store reports in a separate audit/report directory, not inside application source files unless requested.
Suggested structure:
```
reports/
- executive-summary.md
- full-audit-report.md
- findings.csv
- ui-ux-audit.md
- security-audit.md
- remediation-roadmap.md
```
Include the project name, audit date, inspected version or commit when available, scope, tools used, and limitations.

## H. Strict Read-Only Guarantee
Report Mode must not:
- Fix or rewrite source code.
- Apply automatic formatting.
- Modify project configuration.
- Upgrade dependencies.
- Change the database schema or data.
- Modify the application's Git history.
- Deploy the application.
- Make network requests to production systems without authorization.

If a diagnostic tool generates files or modifies caches, use a safe temporary location whenever possible. Clearly disclose any unavoidable side effects before proceeding.
Expected result: A developer can understand the application's strengths, defects, risks, visual problems, and improvement priorities without the application being changed.
