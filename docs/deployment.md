# SAHAJ

SAHAJ is an open-source project that enables flexible setup and deployment of a Consent Management System (CMS) platform via shell scripts and containerization. Instead of relying on a published package, SAHAJ supports source-based, reproducible deployment — ideal for environments where manual control, versioning, or customization is required.

---

## 🌟 What is SAHAJ

SAHAJ provides unified command-line workflows and helper scripts to simplify installation, configuration, and deployment of the CMS platform along with its dependencies (services, workers, DB, message queues, etc.). It is designed for developers and organizations who want to deploy SAHAJ from source — whether for development, testing, staging, or production.  

---

## ✅ Prerequisites

Before deploying SAHAJ from source, make sure your system satisfies the following:

### System Requirements

1.  **Python 3.11+**
    *   Python 3.11.0 or higher is required
    *   Must have `python3-venv` package installed for virtual environment support
    *   Must have `pip` installed for package management
    *   Installation commands (for Debian/Ubuntu):
        ```bash
        sudo apt install python3-venv
        sudo apt install python3-pip
        ```

2.  **Node.js 22+**
    *   Node.js version 22 or higher is required
    *   The `node` command must be available in PATH

3.  **Docker Compose**
    *   Either Docker Compose v2 (`docker compose`) or v1 (`docker-compose`) must be installed
    *   Docker must be running and accessible

4.  **Nginx**
    *   `nginx` must be installed on the system
    *   Installation command (Debian/Ubuntu):
        ```bash
        sudo apt update && sudo apt install -y nginx
        ```

5.  **Certbot (for SSL certificates)**
    *   `certbot` must be installed for issuing SSL certificates
    *   Recommended installation via snap:
        ```bash
        sudo snap install core && sudo snap refresh core
        sudo snap install --classic certbot
        sudo ln -s /snap/bin/certbot /usr/bin/certbot
        ```
    *   Port 80 and 443 should be accessible for Let's Encrypt validation

6.  **OpenSSL (Strongly Recommended)**
    *   `openssl` command-line tool for generating ECDSA keypair
    *   Used to generate:
        *   Private key (SECP256R1/prime256v1)
        *   Public key (derived from private key)
        *   Signing key ID
    *   Installation command:
        ```bash
        sudo apt install openssl
        ```

### Cloudflare DNS Configuration

If you are managing SSL certificates yourself (not using Cloudflare proxy):

*   Type: `A`    Name: `api-cmp`              Content: `your.ip`    Proxy: `DNS only`
*   Type: `A`    Name: `api-dpar`             Content: `your.ip`    Proxy: `DNS only`
*   Type: `A`    Name: `api-notice-worker`    Content: `your.ip`    Proxy: `DNS only`
*   Type: `A`    Name: `api-cookie-consent`   Content: `your.ip`    Proxy: `DNS only`
*   Type: `A`    Name: `cmp`                  Content: `your.ip`    Proxy: `DNS only`
*   Type: `A`    Name: `dpar`                 Content: `your.ip`    Proxy: `DNS only`

Note: If you don't want to handle certbot, you can keep the proxy to `Proxied` (orange cloud in Cloudflare).

---

## 🔧 Prepare Scripts for Execution

Before using any of the provided shell scripts, grant execute permissions:

```bash
find . -name "*.sh" -type f -exec chmod +x {} \;
```

This ensures you can run the scripts directly (e.g. `./scripts/init-rundev.sh`), rather than needing to prefix with `bash`.

---

## 📁 Create `config.json`

A `config.json` is required at the **root** of the project.
Start by copying the example file:

```bash
cp config.json.example config.json
```

Then fill in the values:

```json
{
  "main_domain": "example.com",
  "superadmin_email": "admin@example.com",
  "temporary_password": "Str0ng!Pass1!",
  "df_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Field meanings:**

* **main_domain**: your base domain (no `www`, no subdomains, no http/https).
* **superadmin_email**: admin login email.
* **temporary_password** *(important)*:
  * Must be **strong** or OpenSearch will fail. 
  * Requirements:
    * at least **8 characters**
    * **1 uppercase**
    * **1 lowercase**
    * **1 digit**
    * **1 special character**
  * Example: `Str0ng@Pass1!`
  * You will change this after your first login.
* **df_id**: unique ID (UUID recommended).



---

## 🧪 Local Development Mode

To run SAHAJ locally (for development, testing, debugging):

* Start all services locally:

  ```bash
  ./scripts/init-rundev.sh
  ```

* When finished: cleanly stop services — either retaining data or cleaning volumes for a fresh start:

  * To stop services and clean data/volumes:

    ```bash
    ./scripts/stop-rundev.sh -a
    ```

  * To stop services only (retain data/volumes):

    ```bash
    ./scripts/stop-rundev.sh
    ```

Use the `-a` option when you want to wipe and reset the local state (e.g. between test runs).

---

## 🐳 Containerized / Full Deployment Workflow

For container-based deployment — building Docker images, deploying containers, and managing lifecycle — use the following scripts:

* Build Docker images (without deploying):

  ```bash
  ./scripts/build-images.sh
  ```

* Deploy containers using existing images:

  ```bash
  ./scripts/deploy-all.sh
  ```

* Build images *and* deploy all containers in a single step:

  ```bash
  ./scripts/build-deploy-all.sh
  ```

* Stop all running containers and clean volumes (but keep built images):

  ```bash
  ./scripts/stop-deployed.sh
  ```

* Remove all built images (complete clean-up):

  ```bash
  ./scripts/clean-built-images.sh --yes
  ```

---

## 📦 Typical Workflows

### Development / Local Testing

```bash
# Prepare script permissions (if not already done)
find . -name "*.sh" -type f -exec chmod +x {} \;

# Start local dev environment
./scripts/init-rundev.sh

# … work, test, debug …

# Stop when done — optionally clean data/volumes
./scripts/stop-rundev.sh        # retain data
# or
./scripts/stop-rundev.sh -a     # clean data/volumes
```

### Containerized Deployment / Release / Production-like Setup

```bash
# Build images + deploy all containers
./scripts/build-deploy-all.sh

# When you need to shut down containers:
./scripts/stop-deployed.sh

# To clean up all built images (free disk space / reset build cache):
./scripts/clean-built-images.sh --yes
```

---

Thank you for using SAHAJ! 🎉
