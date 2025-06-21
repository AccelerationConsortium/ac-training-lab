"""
Deployment script for Ax Bayesian Optimization with Prefect and MongoDB checkpointing.

This script creates a Prefect deployment for the optimization workflow,
designed to run continuously on EC2 with automatic restart capability.
"""

from prefect import flow

if __name__ == "__main__":
    # Create deployment for the Ax optimization 
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint="scripts/prefect_scripts/ax_prefect_minimal.py:ax_optimization_flow",
    ).deploy(
        name="ax-bayesian-optimization",
        work_pool_name="my-work-pool",  # Use your configured work pool
        description="Minimal Ax Bayesian Optimization with MongoDB checkpointing",
        tags=["ax", "bayesian-optimization", "mongodb", "checkpoint"],
        parameters={
            "experiment_id": "hartmann6_optimization",
            "max_iterations": 50,
            "resume_from_checkpoint": True
        },
        # Schedule to run continuously
        cron="*/30 * * * *",  # Every 30 minutes
    )
    
    print("✅ Deployment created successfully!")
    print("To run the flow:")
    print("1. Start a worker: prefect worker start --pool my-work-pool")
    print("2. The flow will run automatically every 30 minutes")
    print("3. EC2 restarts will resume from the last MongoDB checkpoint")