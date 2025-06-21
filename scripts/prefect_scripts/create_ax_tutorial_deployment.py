"""
Deployment script for the Ax Bayesian Optimization with Human-in-the-Loop tutorial.

This script creates Prefect deployments for the optimization workflow,
making it easy to schedule and manage optimization runs.
"""

from prefect import flow

if __name__ == "__main__":
    # Create deployment for the Ax optimization tutorial
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint="scripts/prefect_scripts/ax_bayesian_optimization_hitl.py:bayesian_optimization_with_hitl",
    ).deploy(
        name="ax-bayesian-optimization-tutorial",
        work_pool_name="my-managed-pool",  # Use your configured work pool
        description="Ax Bayesian Optimization with Human-in-the-Loop Tutorial",
        tags=["ax", "bayesian-optimization", "human-in-loop", "tutorial"],
        parameters={
            "experiment_name": "ax_tutorial_hartmann6",
            "n_iterations": 10,
            "resume_from_checkpoint": True
        },
        # Optional: Schedule to run weekly for demonstration
        # cron="0 9 * * 1",  # Every Monday at 9 AM
    )
    
    print("✅ Deployment created successfully!")
    print("To run the flow:")
    print("1. Start a worker: prefect worker start --pool my-managed-pool")
    print("2. Trigger a run from the Prefect UI or CLI")
    print("3. Monitor the flow execution and respond to human-in-the-loop prompts")