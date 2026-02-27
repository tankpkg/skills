# Supporting Documentation
Sources: Keep a Changelog, Conventional Commits, GitHub community standards, open source best practices

## CHANGELOG.md
The CHANGELOG.md file provides a curated, chronologically ordered list of notable changes for each version of a project. It helps users and contributors understand exactly what has changed between releases without reading git logs.

### Keep a Changelog Format
Use the standard Keep a Changelog structure. Ensure the file is easy to read and machine-parsable where possible. The structure must be strictly hierarchical, with the version number as an H2 and the change categories as H3.

| Section | Description | Guidance |
| :--- | :--- | :--- |
| **Added** | For new features. | List user-facing features first. |
| **Changed** | For changes in existing functionality. | Document behavioral shifts clearly. |
| **Deprecated** | For soon-to-be removed features. | Include version when removal is planned. |
| **Removed** | For now removed features. | Link to the PR that removed the code. |
| **Fixed** | For any bug fixes. | Include issue number (e.g., #42). |
| **Security** | In case of vulnerabilities. | Link to CVE or security advisory. |

### Semantic Versioning (SemVer)
Tie every release to Semantic Versioning (MAJOR.MINOR.PATCH). This predictability is essential for automated dependency managers.
- **MAJOR**: Incompatible API changes. Example: renaming a public method, changing a required parameter, or removing a exported class.
- **MINOR**: Add functionality in a backwards compatible manner. Example: adding an optional parameter to an existing function or a new helper utility.
- **PATCH**: Backwards compatible bug fixes. Example: fixing a typo in an error message or resolving a memory leak.

### [Unreleased] Section Pattern
Maintain an `[Unreleased]` section at the top of the file to track changes that have been merged to the main branch but not yet tagged in a release. This provides transparency to contributors and users who track the main branch.
- **Link Pattern**: `[Unreleased]: https://github.com/user/repo/compare/v1.2.3...HEAD`
- **Maintenance**: When a new version is released, rename the `[Unreleased]` section to the version number and date, then create a new empty `[Unreleased]` section at the top.

### Breaking Changes and Migration
When introducing a breaking change, document it clearly under the `Changed` or `Removed` section. Provide a brief explanation and a link to a more detailed migration guide if necessary. Use the `[Breaking]` prefix to make these changes stand out.

**Example: Breaking Change Documentation**
```markdown
### Removed
- [Breaking] The `deprecatedMethod()` has been removed. Use `newStableMethod()` instead.
- [Breaking] The `Config` object no longer accepts `string` values; use the `Options` enum.
- The `internalHelper` is no longer exported as it was not intended for public use.

### Changed
- [Breaking] `fetchData()` now returns a Promise instead of taking a callback.
- Improved the performance of the `render()` loop by 15%.
```

### Decision Tree: Version Bumping
1. **Does the change break backwards compatibility?**
   - Yes: Increment **MAJOR** (e.g., 1.2.3 -> 2.0.0).
2. **Does the change add new functionality without breaking anything?**
   - Yes: Increment **MINOR** (e.g., 1.2.3 -> 1.3.0).
3. **Does the change fix a bug or improve performance without changing behavior?**
   - Yes: Increment **PATCH** (e.g., 1.2.3 -> 1.2.4).
4. **Is it a documentation-only change?**
   - Most projects bump **PATCH**, but some use `v1.2.3-docs.1` for intermediate updates.
5. **Is it a pre-release?**
   - Use suffixes like `-alpha.1`, `-beta.2`, or `-rc.1`.

## CONTRIBUTING.md
The CONTRIBUTING.md file defines the standards for participation. It reduces friction for new contributors by providing clear instructions on how to help and ensures that the maintainers receive high-quality contributions.

### Essential Sections
- **How to report a bug**: Provide a link to the issue tracker and specify required info (steps to reproduce, environment). Use a bug report template if available.
- **How to suggest a feature**: Explain the process for proposing new ideas. Encourage users to search for existing issues first.
- **Pull Request process**: Detail the steps from branch creation to merge. Include information on who is responsible for merging.

### Development Setup
Provide exact, copy-pasteable commands for setting up the local environment. Include troubleshooting tips for common platform issues (e.g., Windows path issues, M1 Mac compatibility).
1. **Fork and clone**: `git clone https://github.com/your-username/repo.git`.
2. **Install dependencies**: `npm install` or `pip install -r requirements.txt`. Use lockfiles (e.g., `package-lock.json`) to ensure environment parity.
3. **Configure environment**: Copy `.env.example` to `.env` and fill in secrets.
4. **Run the build**: `npm run build` or `make build`.
5. **Run tests**: `npm test` or `pytest`.

### Code Style Requirements
Reference the project's linting and formatting tools.
- **Linter**: ESLint (JavaScript/TS), Pylint (Python), RuboCop (Ruby).
- **Formatter**: Prettier, Black, Gofmt.
- **Automation**: Mention that linting is enforced via CI and pre-commit hooks.
- **Naming**: Specify casing (camelCase for variables, PascalCase for classes).

### Conventional Commits Format
Require contributors to use the Conventional Commits specification. This allows for automated changelog generation and versioning.
- `feat`: A new feature (correlates with MINOR in SemVer).
- `fix`: A bug fix (correlates with PATCH in SemVer).
- `docs`: Documentation only changes.
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Updating build tasks, package manager configs, etc.

### PR Process and Review
- **Branching**: Create a feature branch from `main` (e.g., `feat/add-user-auth`).
- **Commits**: Use clear messages and sign-off if required.
- **Tests**: Ensure all existing tests pass and new code is covered.
- **PR Description**: Explain the "why" behind the change, not just the "what". Link to related issues.
- **Review**: Be responsive to feedback. Once approved, the maintainer will merge (or ask you to rebase).

### "Good First Issues" Pattern
Encourage new contributors by tagging simple tasks as `good first issue`. Provide a direct link in the CONTRIBUTING.md: `[View good first issues](https://github.com/org/repo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)`. This lowers the barrier to entry for first-time contributors.

### Testing Requirements
Define the expected test coverage (e.g., 80%+).
- **Unit Tests**: Focus on individual functions and logic.
- **Integration Tests**: Focus on module interactions.
- **E2E Tests**: Focus on the full user flow (using Playwright or Cypress).
- **Performance Tests**: For critical paths that must remain fast.

### License Agreement (DCO or CLA)
Specify if contributors need to sign a Contributor License Agreement (CLA) or use the Developer Certificate of Origin (DCO).
- **DCO**: Simple sign-off in commit message (`Signed-off-by: Name <email>`).
- **CLA**: More formal legal agreement, often used by corporate-backed projects (e.g., Google, Microsoft).

## LICENSE
A LICENSE file is mandatory for open-source projects. Without it, the default copyright laws apply, meaning you retain all rights and others cannot legally use your code.

### Common Licenses for Libraries
| License | Type | Key Characteristic | Use Case |
| :--- | :--- | :--- | :--- |
| **MIT** | Permissive | Short, simple, allows almost anything. | Max adoption. |
| **Apache 2.0** | Permissive | Includes patent grants and protection. | Corporate projects. |
| **ISC** | Permissive | Functionally identical to MIT, shorter. | Minimalists. |
| **BSD 3-Clause** | Permissive | Requires attribution and non-endorsement. | Scientific software. |
| **MPL 2.0** | Weak Copyleft | File-level copyleft; easy to mix with closed source. | Large libraries. |
| **Unlicense** | Public Domain | Dedicates work to the public domain. | "No rights reserved". |

### Decision Tree: Choosing a License
1. **Do you want it to be as simple as possible?** -> **MIT**
2. **Do you need patent protection for your users?** -> **Apache 2.0**
3. **Do you want to force derivative works to be open source?** -> **GPL v3**
4. **Do you want a balance of open source and commercial use?** -> **MPL 2.0**
5. **Are you building a small snippet or config?** -> **Unlicense**

### License Badge and Header
- **Badge**: Include a badge at the top of the README (e.g., using shields.io).
- **File Header**: It is good practice to include a short license header at the top of every source file.

## CODE_OF_CONDUCT.md
This file establishes expectations for behavior within the project community. It signals that the project is a safe and welcoming space for everyone.

### Contributor Covenant
The Contributor Covenant is the industry standard template.
- **Selection**: Always use the latest version (currently 2.1).
- **Customization**: Fill in the `contact_address` with a private email (e.g., `conduct@example.com`).

### Inclusion and Enforcement
A Code of Conduct is necessary for any project that accepts external contributions. It must include an enforcement section that details:
- **Reporting**: Clear steps on how to report an incident.
- **Review**: How the report will be reviewed and by whom.
- **Consequences**: A graduated scale of responses, from a private reprimand to permanent expulsion.
- **Transparency**: Periodic anonymized reports on enforcement actions (for large projects).

## SECURITY.md
The SECURITY.md file outlines how users should report security vulnerabilities. It prevents public disclosure of zero-day exploits.

### Responsible Disclosure Process
Instruct users to report vulnerabilities privately.
- **Method**: Use GitHub's "Private vulnerability reporting" or a secure email.
- **Timeline**: Specify the expected response time (e.g., "We will acknowledge your report within 48 hours").
- **Bug Bounty**: Mention if the project participates in any bounty programs (e.g., HackerOne).

### Supported Versions Table
Maintain a table showing which versions are currently receiving security updates.

| Version | Status | Security Updates |
| :--- | :--- | :--- |
| v3.x | Current | Yes (Full Support) |
| v2.5.x | Active | Yes (Security Only) |
| v2.4.x | EOL | No |
| v1.x | Legacy | No |

### Security Policy Checklist
- Define what constitutes a security vulnerability.
- List supported versions.
- Provide private contact info.
- Outline the fix/disclosure timeline.
- Detail the process for credits and attribution.

## docs/ Directory Structure
For complex projects, move detailed documentation from the README into a `docs/` folder to maintain scannability and provide a better learning experience.

### Suggested Hierarchy
- `docs/getting-started/`: Quick start, installation, "Hello World" example.
- `docs/guides/`: Thematic guides (e.g., "Authentication", "Deployment", "Extending the CLI").
- `docs/api/`: Technical reference for all exported members, often auto-generated from JSDoc/Docstrings.
- `docs/examples/`: Realistic use cases, integrated recipes, and sample projects.
- `docs/troubleshooting/`: FAQ and common error solutions.

### Documentation Tooling
If the `docs/` folder grows large, consider using a static site generator.
- **Docusaurus**: Best for React-based documentation with search.
- **MkDocs**: Simple, Python-based, uses Markdown.
- **VitePress**: Fast, Vue-based, ideal for modern JS projects.
- **GitHub Pages**: Host your `docs/` folder directly on a custom subdomain.

### Cross-Linking and Navigation
- **Relative Links**: Use `[Installation](./getting-started/installation.md)` to ensure links work in the GitHub UI.
- **Sidebar**: Maintain a `SUMMARY.md` or `_sidebar.md` if using tools like Docsify or GitBook.

## .github/ Templates
Templates standardize the information provided by users, making issues and PRs significantly easier to triage and resolve.

### Issue Templates (Markdown vs YAML)
- **Markdown**: Simple, but users often delete the prompts.
- **YAML (Issue Forms)**: Modern, structured forms that enforce required fields and use dropdowns/checkboxes.
  - Path: `.github/ISSUE_TEMPLATE/bug_report.yml`.

### Example Bug Report Template (YAML)
```yaml
name: Bug Report
description: File a bug report to help us improve
body:
  - type: markdown
    attributes:
      value: "Thanks for taking the time to fill out this bug report!"
  - type: textarea
    id: repro
    attributes:
      label: Steps to Reproduce
      placeholder: 1. Go to...
    validations:
      required: true
  - type: dropdown
    id: version
    attributes:
      label: Version
      options:
        - v3.0.0
        - v2.9.1
```

### Pull Request Template
Include a checklist in the PR template to ensure contributors don't forget essential steps:
- **Type**: (Feat/Fix/Docs/Style)
- **Tests**: (New tests added? Existing tests pass?)
- **Docs**: (Updated README or `docs/`?)
- **Breaking**: (Does this require a MAJOR version bump?)
- **Issue**: (Fixes #123)

### FUNDING.yml
Use this file to display a "Sponsor" button on the repository.
- **Platforms**: `github: [user]`, `open_collective: [slug]`, `patreon: [user]`, `custom: ['https://example.com/donate']`.

## Migration Guides
Migration guides are critical when releasing breaking changes. They reduce the friction of upgrading to a new major version.

### Structure of a Migration Guide
1. **Introduction**: Explicitly state the version change (e.g., v2 to v3).
2. **What Changed**: List the high-level reasons for the break (e.g., "Moving to ESM").
3. **Automated Migration**: If available, provide a codemod (e.g., `npx my-lib-migrate`).
4. **Step-by-Step Upgrade**: Specific tasks the user must perform.
5. **Before/After Code Blocks**: The most valuable part for developers.

### Common Pitfalls and Troubleshooting
Include a section on common errors encountered during migration and how to resolve them. This prevents duplicate issues in your tracker.

## Decision Matrix: Documentation Essentials
Use this matrix to determine which files are required based on project maturity and target audience.

| File | Small Utility | Mid-Size Library | Major Framework |
| :--- | :---: | :---: | :---: |
| **README.md** | Required | Required | Required |
| **LICENSE** | Required | Required | Required |
| **CHANGELOG.md** | Recommended | Required | Required |
| **CONTRIBUTING.md** | Optional | Required | Required |
| **CODE_OF_CONDUCT.md**| Optional | Recommended | Required |
| **SECURITY.md** | Optional | Recommended | Required |
| **.github/templates** | Optional | Recommended | Required |
| **docs/ folder** | No | Recommended | Required |
| **Migration Guide** | No | If breaking | Required |
| **FUNDING.yml** | Optional | Optional | Recommended |
| **ROADMAP.md** | No | Optional | Recommended |

