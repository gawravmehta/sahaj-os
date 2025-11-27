# SAHAJ

SAHAJ is an open-source project that enables flexible setup and deployment of a Consent Management System (CMS) platform via shell scripts and containerization. Instead of relying on a published package, SAHAJ supports source-based, reproducible deployment — ideal for environments where manual control, versioning, or customization is required.

---

## 🌟 What is SAHAJ

SAHAJ provides unified command-line workflows and helper scripts to simplify installation, configuration, and deployment of the CMS platform along with its dependencies (services, workers, DB, message queues, etc.). It is designed for developers and organizations who want to deploy SAHAJ from source — whether for development, testing, staging, or production.  

---

## ✅ Prerequisites

Before deploying SAHAJ from source, make sure your system satisfies the following:

- Unix-like operating system (Linux or macOS), or Windows with a compatible shell (e.g. WSL, bash, sh)  
- Shell (bash or sh) available  
- Docker (and optionally Docker Compose) installed — if you plan to use containerized deployment  
- A clone of the SAHAJ source repository, including the `scripts/` directory  
- (Optional but recommended) A Python virtual environment for running backend code locally  

```bash
python3 -m venv env
source env/bin/activate   # On Windows: env\Scripts\activate  
```

---

## 🔧 Prepare Scripts for Execution

Before using any of the provided shell scripts, grant execute permissions:

```bash
find . -name "*.sh" -type f -exec chmod +x {} \;
```

This ensures you can run the scripts directly (e.g. `./scripts/init-rundev.sh`), rather than needing to prefix with `bash`.

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
  ./scripts/clean-built-images.sh
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
./scripts/clean-built-images.sh
```

---

Thank you for using SAHAJ! 🎉
