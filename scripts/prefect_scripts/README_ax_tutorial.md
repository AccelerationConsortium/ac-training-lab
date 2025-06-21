# Ax Bayesian Optimization with Prefect Human-in-the-Loop Tutorial

This tutorial demonstrates how to integrate Ax (Adaptive Experimentation Platform) with Prefect for human-in-the-loop Bayesian optimization workflows, including checkpointing to MongoDB and restart capabilities.

## 🎯 What You'll Learn

- Setting up Bayesian optimization with Ax
- Integrating human decision-making into automated workflows
- Implementing robust checkpointing with MongoDB
- Building restart-capable optimization workflows
- Using Prefect for workflow orchestration and monitoring

## 📁 Files in This Tutorial

- **`ax_bayesian_optimization_hitl.py`** - Main tutorial script with complete workflow
- **`test_ax_tutorial_setup.py`** - Test script to verify your setup
- **`create_ax_tutorial_deployment.py`** - Deployment script for Prefect
- **`../docs/ax_tutorial_setup.md`** - Detailed setup instructions

## 🚀 Quick Start

### 1. Test Your Setup

First, verify that your environment is correctly configured:

```bash
cd scripts/prefect_scripts
python test_ax_tutorial_setup.py
```

This will check if all required packages are available and test basic functionality.

### 2. Run the Tutorial

```bash
python ax_bayesian_optimization_hitl.py
```

The tutorial will:
- Start a Bayesian optimization of the Hartmann6 function
- Periodically pause for human input
- Save checkpoints to MongoDB (or local files as fallback)
- Allow you to continue, stop, or modify the optimization

### 3. Deploy to Prefect (Optional)

To run this as a managed Prefect flow:

```bash
python create_ax_tutorial_deployment.py
prefect worker start --pool my-managed-pool
```

Then trigger runs from the Prefect UI.

## 🔧 Configuration

### Environment Variables

```bash
# MongoDB connection (required for persistence)
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"
export MONGODB_DATABASE="ax_tutorial"
export MONGODB_COLLECTION="optimization_checkpoints"
```

### Tutorial Parameters

Edit these variables in `ax_bayesian_optimization_hitl.py`:

```python
EXPERIMENT_NAME = "ax_tutorial_hartmann6"  # Name of your experiment
N_ITERATIONS = 10                          # Number of optimization iterations
MIN_CONFIDENCE_THRESHOLD = 0.8             # When to ask for human input
```

## 🎛️ Human-in-the-Loop Interface

During optimization, you'll be prompted with:

```
🧪 Optimization Update - Iteration 3

📊 Current Best:
   • Objective Value: -2.1234
   • Parameters: {'x1': 0.123, 'x2': 0.456, ...}

🎯 Latest Trial:
   • Parameters: {'x1': 0.789, 'x2': 0.012, ...}
   • Objective: -1.9876

🤖 Algorithm Confidence: 67%

Should we continue optimization?
```

You can then:
- ✅ Continue optimization
- 🛑 Stop the process
- 📝 Add comments and observations
- 🔧 Suggest parameter adjustments
- 🎯 Override confidence assessments

## 📊 Monitoring Progress

### Prefect UI
- View real-time flow execution
- See all human interactions
- Monitor task performance
- Access detailed logs

### MongoDB Data
Query your optimization data:

```python
from pymongo import MongoClient

client = MongoClient("your_connection_string")
db = client["ax_tutorial"]
collection = db["optimization_checkpoints"]

# Get all experiments
experiments = list(collection.find({}))
print(f"Found {len(experiments)} checkpoints")

# Get best result
best = min(experiments, key=lambda x: x['best_objective'])
print(f"Best objective: {best['best_objective']}")
```

## 🔄 Restart Capabilities

The tutorial automatically handles interruptions:

1. **Graceful Restart**: If stopped cleanly, resume from the last checkpoint
2. **Error Recovery**: Human intervention on errors with continue/stop options
3. **State Persistence**: All optimization state saved to MongoDB
4. **Parameter Continuity**: Maintains Ax's internal model state

To restart an interrupted optimization:

```python
# The tutorial automatically detects and resumes from checkpoints
python ax_bayesian_optimization_hitl.py
```

## 🧪 Example Optimization Problem

The tutorial optimizes the **Hartmann6 function**, a standard 6-dimensional benchmark:

- **Dimensions**: 6 parameters (x1, x2, x3, x4, x5, x6)
- **Domain**: Each parameter in [0, 1]
- **Objective**: Minimize f(x) (known global minimum ≈ -3.32)
- **Challenge**: Multiple local minima, requires smart exploration

## 📈 Expected Results

A typical optimization run might look like:

```
Iteration 1: objective = -0.456, confidence = 10%
Iteration 2: objective = -1.234, confidence = 25%
[Human input requested - low confidence]
Iteration 3: objective = -2.100, confidence = 40%
Iteration 4: objective = -2.890, confidence = 60%
...
Iteration 10: objective = -3.201, confidence = 95%

Best found: f(x) = -3.201 at x = [0.201, 0.150, 0.477, 0.275, 0.312, 0.657]
```

## 🔧 Customization

### Replace the Objective Function

To optimize your own function, replace the `hartmann6_objective` function:

```python
def my_objective(parameters: Dict[str, float]) -> float:
    """Your custom objective function."""
    # Your optimization logic here
    x1, x2, x3 = parameters['x1'], parameters['x2'], parameters['x3']
    return some_expensive_computation(x1, x2, x3)

# Update the parameter space in initialize_ax_client
ax_client.create_experiment(
    name=experiment_name,
    parameters=[
        {"name": "x1", "type": "range", "bounds": [0.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [-5.0, 5.0]},
        {"name": "x3", "type": "choice", "values": ["A", "B", "C"]},
    ],
    objective_name="my_objective",
    minimize=True,  # or False for maximization
)
```

### Add Constraints

```python
# Add parameter constraints
ax_client.create_experiment(
    # ... other parameters ...
    parameter_constraints=["x1 + x2 <= 1.0"],  # Linear constraints
)
```

### Customize Human Input

Modify the `HumanInput` class to collect different information:

```python
class HumanInput(RunInput):
    continue_optimization: bool = True
    quality_assessment: str = ""  # "poor", "good", "excellent"
    suggested_focus_area: str = ""
    risk_tolerance: float = 0.5  # 0 = conservative, 1 = aggressive
```

## 🐛 Troubleshooting

### Common Issues

1. **"Ax not available"** - Install with `pip install ax-platform` or use the mock implementation
2. **MongoDB connection fails** - Check connection string and ensure MongoDB is running
3. **Prefect authentication errors** - Run `prefect cloud login` again
4. **Human input timeouts** - Increase timeout values in `pause_flow_run` calls

### Getting Help

- Check the detailed setup guide: `docs/ax_tutorial_setup.md`
- Run the test script: `python test_ax_tutorial_setup.py`
- Review Prefect logs in the UI
- Check MongoDB logs for connection issues

## 📚 Further Reading

- [Ax Documentation](https://ax.dev/)
- [Prefect Interactive Workflows](https://www.prefect.io/blog/unveiling-interactive-workflows)
- [Bayesian Optimization Explained](https://distill.pub/2020/bayesian-optimization/)
- [MongoDB with Python](https://pymongo.readthedocs.io/)

## 🤝 Contributing

This tutorial is part of the AC Training Lab. To contribute:

1. Fork the repository
2. Make your improvements
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This tutorial follows the same license as the AC Training Lab repository.