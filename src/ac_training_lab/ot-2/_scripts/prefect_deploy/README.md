# Prefect Deploy Example - Work Pools and Work Queues

This directory contains a complete example of using Prefect 3 with work pools and work queues for OT-2 device orchestration.

## Overview

This setup uses Prefect's work pool infrastructure to securely manage laboratory device operations. Instead of using `serve()` which requires broad deployment permissions, we use `deploy()` with work pools that allow fine-grained access control.

## Architecture

- **Work Pool**: `ot2-device-pool` (process type) - manages execution on OT-2 devices
- **Work Queues**:
  - `high-priority`: For urgent operations like color mixing
  - `standard`: For regular measurements
  - `low-priority`: For cleanup and reset operations
- **Workers**: Run on individual devices, poll the work pool for jobs
- **Deployments**: Pre-configured flows assigned to specific queues

## Setup Instructions

### 1. Install Dependencies
```bash
pip install prefect
```

### 2. Set up Work Pool and Queues
Run this once with appropriate permissions:
```bash
python setup_work_pool.py
```

Or manually:
```bash
# Create work pool
prefect work-pool create ot2-device-pool --type process --description "Work pool for OT-2 devices"

# Create work queues with priorities
prefect work-queue create high-priority --pool ot2-device-pool --priority 1 --description "High priority queue"
prefect work-queue create standard --pool ot2-device-pool --priority 2 --description "Standard priority queue"
prefect work-queue create low-priority --pool ot2-device-pool --priority 3 --description "Low priority queue"
```

### 3. Create Deployments
Choose one method:

**Option A: Python API**
```bash
python deploy.py
```

**Option B: CLI with prefect.yaml**
```bash
prefect deploy
```

### 4. Start Workers on Devices
On each OT-2 device, start a worker (run in background):
```bash
# For high-priority operations
prefect worker start --pool ot2-device-pool --queue high-priority

# For standard operations
prefect worker start --pool ot2-device-pool --queue standard

# For low-priority operations
prefect worker start --pool ot2-device-pool --queue low-priority

# Or start a worker that can handle all queues
prefect worker start --pool ot2-device-pool
```

### 5. Submit Jobs
Run the orchestrator to submit jobs:
```bash
python orchestrator.py
```

## Security Benefits

- **Separation of Concerns**: Deployment creation (admin) vs. execution (device)
- **Queue-based Access**: Devices only execute jobs from their assigned queues
- **No Broad Permissions**: Workers don't need deployment creation rights
- **Scalable**: Multiple devices can share the same work pool with different queues

## Best Practices

- **Working Directories**: All paths are relative to project root
- **Queue Naming**: Use descriptive names for different device types/priorities
- **Concurrency**: Set concurrency limits on queues to prevent resource conflicts
- **Monitoring**: Use Prefect UI to monitor queue status and job execution
- **Versioning**: Update deployments when flow parameters change

## Files Overview

- `flows.py`: Flow definitions with OT-2 operations
- `setup_work_pool.py`: Work pool and queue creation script
- `deploy.py`: Deployment creation using Python API
- `prefect.yaml`: Alternative deployment configuration
- `orchestrator.py`: Job submission script with prioritization examples

## Adapting for Other Devices

To add more devices/queues:
1. Create additional work queues in `setup_work_pool.py`
2. Add corresponding deployments in `deploy.py` or `prefect.yaml`
3. Start workers on new devices targeting specific queues
4. Update `orchestrator.py` to submit jobs to new queues

This pattern scales well for multiple laboratory devices with different capabilities and priorities.
