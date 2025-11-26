# Contributing to the Consent Management System

Thank you for considering contributing to our Consent Management System! We welcome contributions from everyone. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

There are many ways to contribute, from reporting bugs to writing documentation, submitting feature requests, or writing code.

### Reporting Bugs

* Ensure the bug hasn't already been reported.
* Open a new issue with a clear title and description.
* Include steps to reproduce the bug, expected behavior, and actual behavior.
* Provide relevant environment details (OS, browser, etc.).

### Suggesting Enhancements

* Open a new issue with a clear title and detailed description of the proposed enhancement.
* Explain why this enhancement would be useful.
* If applicable, provide mock-ups or examples.

### Code Contributions

1.  **Fork the Repository**: Start by forking the `sahaj-os` repository to your GitHub account.
2.  **Clone Your Fork**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/sahaj-os.git
    cd sahaj-os
    ```
3.  **Create a New Branch**:
    ```bash
    git checkout -b feature/your-feature-name-or-bugfix/your-bugfix-name
    ```
    Choose a descriptive name for your branch (e.g., `feature/add-cookie-banner`, `bugfix/fix-consent-logging`).
4.  **Set up Your Development Environment**:
    Refer to the `docs/setup.md` file for instructions on how to set up your local development environment.
5.  **Make Your Changes**: Write your code, ensuring it adheres to our coding standards.
6.  **Test Your Changes**: Run existing tests and add new ones if necessary to cover your changes.
7.  **Commit Your Changes**:
    ```bash
    git commit -m "feat: Add concise description of your feature"
    ```
    (Use `fix:` for bug fixes, `docs:` for documentation, `refactor:` for refactoring, etc.)
8.  **Push to Your Fork**:
    ```bash
    git push origin feature/your-feature-name-or-bugfix/your-bugfix-name
    ```
9.  **Create a Pull Request (PR)**:
    *   Go to the original `sahaj-os` repository on GitHub.
    *   You should see a prompt to create a new Pull Request from your recently pushed branch.
    *   Provide a clear and detailed description of your changes in the PR description.
    *   Reference any relevant issues (e.g., `Fixes #123`, `Closes #456`).

## Coding Standards

*   **Language Specific Guidelines**: Follow the established coding conventions for Python (PEP 8) and JavaScript/TypeScript (ESLint/Prettier configurations).
*   **Documentation**: Document your code thoroughly, especially complex functions, modules, and APIs.
*   **Comments**: Use comments to explain *why* certain decisions were made, not just *what* the code does.

## Data Privacy and Security Considerations

As this is a Consent Management System, all contributions must prioritize data privacy and security.

*   **Privacy-by-Design**: Ensure all new features and changes are designed with privacy in mind from the outset.
*   **Security-by-Design**: Implement secure coding practices to prevent vulnerabilities.
*   **Compliance**: Be aware of and adhere to relevant data protection regulations (e.g., GDPR, CCPA).
*   **Data Handling**: Do not introduce any code that could unintentionally expose or misuse personal data.
*   **Testing**: Include tests specifically for privacy and security aspects where applicable.

## Testing

*   **Unit Tests**: Write unit tests for new functions and components.
*   **Integration Tests**: Add integration tests for features that involve multiple components.
*   **End-to-End Tests**: For UI changes, consider how to add or update end-to-end tests.
*   **Privacy/Security Tests**: When adding features that handle sensitive data, ensure appropriate tests are in place to validate data protection measures.

## Review Process

*   All pull requests will be reviewed by maintainers.
*   Be prepared to receive feedback and make iterative changes.
*   We aim for a constructive and collaborative review process.

Thank you for helping us build a robust and privacy-respecting Consent Management System!
