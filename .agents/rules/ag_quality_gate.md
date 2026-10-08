# Quality Gate Checklist: Chemistry

Before declaring ANY task or project complete, you MUST execute the following verification cycle:

1. **Requirements & Architecture Review**
2. **Implementation Verification**
3. **Build & Syntax Verification**
4. **Automated Tests** (unit, integration, regression)
5. **Security Audit** (no plaintext credentials, injection checks, input validation)
6. **UI/UX & Accessibility Review** (semantic elements, responsive behavior, contrast)
7. **Documentation & Changelog**

### Mode-Specific Quality Gates:
- [ ] Chemical equations balanced by mass and charge
- [ ] Safety hazards (MSDS) listed for all reagents
- [ ] Limiting reagents calculated

### Error Policy & Reporting:
Never falsely claim 'zero errors'. Classify any findings into:
- `CRITICAL`: High-risk vulnerabilities, crashes, data corruption
- `HIGH`: Broken core functionality, missing authentication
- `MEDIUM`: UI inconsistencies, edge-case validation misses
- `LOW`: Minor cosmetic issues, non-critical warnings
- `INFO`: Suggestions for future enhancement