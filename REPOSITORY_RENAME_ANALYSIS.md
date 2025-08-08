# Repository Renaming Impact Analysis: "ac-training-lab" to "ac-dev-lab"

## Executive Summary

**Repository:** AccelerationConsortium/ac-training-lab → AccelerationConsortium/ac-dev-lab  
**Impact Scope:** 90+ files across repository + 20+ device clones + external integrations  
**Migration Complexity:** Medium (2-4 hours internal changes + extensive external coordination)  
**Risk Level:** Low for internal changes, **High** for external dependencies and established branding

## Key Findings

### 1. Repository-Internal Impact (90+ files)

**Core Configuration Files:**
- `setup.cfg` - Package name, URLs, project metadata
- `pyproject.toml` - Build system configuration  
- `environment.yml` - Conda environment name
- `Dockerfile` - Container build references
- `.readthedocs.yaml` - Documentation build configuration

**Documentation (25+ files):**
- `README.md` - Main project description and badges
- `CONTRIBUTING.md` - Contributor guidelines
- `docs/` directory - All documentation pages
- Device-specific README files (17 found)
- Multiple badge URLs in README (ReadTheDocs, GitHub Actions, etc.)

**Source Code Impact:**
- **Complete package rename:** `src/ac_training_lab/` → `src/ac_dev_lab/`
- **25+ Python files** with import statements requiring updates
- **Scripts and automation:** Prefect deployments, CI/CD workflows
- **Test files:** Import statements and test configurations

### 2. External Dependencies & Established Branding

**Critical External Integrations:**
- **ReadTheDocs:** ac-training-lab.readthedocs.io (public documentation site)
- **Course Materials:** University of Toronto partnership course titled "Acceleration Consortium Training Lab Design Project"
- **Academic Credentials:** Micro-credential certification using exact terminology
- **Published References:** News releases, academic communications
- **GitHub Ecosystem:** Listed as flagship project on Acceleration Consortium main page

**User Impact (Expanded Scope):**
- **20+ device clones** requiring git remote URL updates (as noted by @sgbaird)
- Contributors need to update development environments
- Bookmark and reference updates across team

### 3. Organizational Context & Naming Considerations

Based on feedback from @sgbaird, there are three distinct teams/labs within the organization:

1. **"AI & Automation Lab"** - Research-focused, less deployment-oriented
2. **"Orchestration Team"** - Workflow and data orchestration focus  
3. **This repository's focus** - Hardware-focused + device integration

**Naming Analysis:**
- Current: "ac-training-lab" - Focused but potentially limiting scope
- Proposed: "ac-dev-lab" - More inclusive of development beyond training
- Context: Hardware/device integration focus distinguishes from other teams

## Detailed Impact Assessment

### Repository Files Requiring Updates

| Category | Files | Update Type |
|----------|-------|-------------|
| **Package Configuration** | setup.cfg, pyproject.toml, environment.yml | Package name, URLs |
| **Documentation** | README.md, CONTRIBUTING.md, docs/ (20+ files) | Text, URLs, badges |
| **Source Code** | src/ac_training_lab/ (25+ Python files) | Directory rename, imports |
| **CI/CD & Scripts** | .github/, scripts/ (10+ files) | Workflow references |
| **Container & Deploy** | Dockerfile, prefect scripts | Image names, deployment configs |

### External Service Coordination Required

| Service | Current | New | Migration Required |
|---------|---------|-----|-------------------|
| ReadTheDocs | ac-training-lab.readthedocs.io | ac-dev-lab.readthedocs.io | ✅ High Priority |
| GitHub Repository | /ac-training-lab | /ac-dev-lab | ✅ Automatic redirects |
| Course Materials | "Training Lab Design Project" | Update title/references | ⚠️ Academic coordination |
| Published Content | News, papers, credentials | Update references | ⚠️ External stakeholders |

### Risk Assessment Matrix

| Risk Category | Probability | Impact | Mitigation |
|---------------|-------------|---------|------------|
| **Internal file updates** | Low | Low | Automated scripts, testing |
| **20+ device clone updates** | Medium | Medium | Communication plan, documentation |
| **ReadTheDocs URL changes** | Medium | Medium | Subdomain migration, redirects |
| **Course material disruption** | Medium | High | Academic partner coordination |
| **Published reference confusion** | High | High | Stakeholder communication |
| **Credential/certification impact** | High | High | Academic institution coordination |

## Updated Naming Recommendations

Given the organizational context (hardware/device integration focus) and existing team names:

1. **ac-hardware-lab** (NEW - Distinguishes from AI/Orchestration teams)
2. **ac-device-lab** (NEW - Emphasizes device integration focus)  
3. **ac-dev-lab** (Original proposal - General development)
4. **ac-integration-lab** (NEW - Highlights integration work)
5. **ac-prototype-lab** (Alternative - Prototyping focus)

## Migration Strategy

### Phase 1: Preparation & External Coordination (1-2 weeks)
- [ ] Coordinate with University of Toronto course administrators
- [ ] Plan ReadTheDocs subdomain migration
- [ ] Notify all 20+ device clone users
- [ ] Assess academic credential/publication impact
- [ ] Create comprehensive communication plan

### Phase 2: Repository Internal Changes (2-4 hours)
- [ ] Update package configuration files
- [ ] Rename source directory and update all imports
- [ ] Update documentation and README badges
- [ ] Update CI/CD workflows and scripts
- [ ] Update container and deployment configurations

### Phase 3: External Service Updates (1-2 days)
- [ ] Perform GitHub repository rename (triggers redirects)
- [ ] Migrate ReadTheDocs configuration
- [ ] Update external badge URLs
- [ ] Test all documentation links

### Phase 4: Academic & External Updates (Ongoing)
- [ ] Update course syllabi and materials
- [ ] Coordinate credential terminology updates
- [ ] Update published references where possible
- [ ] Monitor for broken external integrations

### Phase 5: User Transition Support (2-4 weeks)
- [ ] Support 20+ device clone updates
- [ ] Provide migration guides
- [ ] Monitor for issues and provide assistance
- [ ] Update any missed external references

## Recommendation

**PROCEED WITH CAUTION** - While the technical migration is feasible, the established branding in academic courses, credentials, and published materials creates significant external dependencies. 

**Recommended Approach:**
1. **Consider "ac-hardware-lab" over "ac-dev-lab"** to better distinguish from other organizational teams
2. **Coordinate extensively with academic partners** before proceeding
3. **Plan for 4-6 week migration timeline** including external coordination
4. **Ensure all 20+ device users are properly notified and supported**

The rebranding benefits must be weighed against the disruption to established academic programs and published credentials. Consider whether the current name truly limits the project's scope enough to justify the coordination effort required.

## Migration Checklist

<details>
<summary>Complete file-by-file checklist (click to expand)</summary>

### Configuration Files
- [ ] `setup.cfg` - name, url, project_urls, documentation
- [ ] `pyproject.toml` - if package name referenced
- [ ] `environment.yml` - environment name
- [ ] `.readthedocs.yaml` - project configuration

### Documentation  
- [ ] `README.md` - title, description, all badge URLs
- [ ] `CONTRIBUTING.md` - repository references
- [ ] `docs/index.md` - main documentation page
- [ ] `docs/conf.py` - Sphinx configuration
- [ ] All device README files (17+ files)

### Source Code
- [ ] Rename `src/ac_training_lab/` to `src/ac_dev_lab/`
- [ ] Update all Python imports (25+ files found)
- [ ] Update test files in `tests/`
- [ ] Update script references in `scripts/`

### CI/CD & Automation
- [ ] `.github/workflows/` - workflow files
- [ ] `scripts/prefect_scripts/` - deployment scripts
- [ ] `Dockerfile` - container references
- [ ] Any deployment configurations

### External Services
- [ ] ReadTheDocs project rename
- [ ] GitHub repository rename
- [ ] Update external badge services
- [ ] Coordinate course material updates

</details>

---

**Analysis Completed:** $(date)  
**Scope:** Repository rename impact assessment per issue #415  
**Contact:** Development team for technical questions, academic partners for external coordination