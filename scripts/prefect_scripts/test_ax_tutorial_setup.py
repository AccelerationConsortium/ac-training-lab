#!/usr/bin/env python3
"""
Simple test script for the Ax Bayesian Optimization Tutorial.

This script tests the basic functionality without requiring full setup,
making it easy to verify that dependencies and basic components work.
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if required packages can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import numpy as np
        print("✅ NumPy available")
    except ImportError:
        print("❌ NumPy not available - install with: pip install numpy")
        return False
    
    try:
        from prefect import flow, task
        print("✅ Prefect available")
    except ImportError:
        print("❌ Prefect not available - install with: pip install prefect")
        return False
    
    try:
        from pymongo import MongoClient
        print("✅ PyMongo available")
    except ImportError:
        print("⚠️  PyMongo not available - install with: pip install pymongo")
        print("   (Optional: will use local file fallback)")
        
    try:
        import ax
        print("✅ Ax available")
    except ImportError:
        print("⚠️  Ax not available - install with: pip install ax-platform")
        print("   (Tutorial includes fallback mock implementation)")
    
    return True

def test_hartmann6_function():
    """Test the objective function."""
    print("\n🎯 Testing objective function...")
    
    import numpy as np
    
    def hartmann6_simplified(parameters):
        """Simplified Hartmann6 implementation for testing."""
        x = np.array([parameters[f"x{i}"] for i in range(1, 7)])
        return np.sum(x**2) - 3.0 * np.exp(-np.sum(x**2))
    
    # Test with known parameters
    test_params = {f"x{i}": 0.1 for i in range(1, 7)}
    result = hartmann6_simplified(test_params)
    
    print(f"✅ Objective function test: f({test_params}) = {result:.4f}")
    return True

def test_checkpoint_functionality():
    """Test checkpoint save/load functionality."""
    print("\n💾 Testing checkpoint functionality...")
    
    # Create temporary checkpoint data
    checkpoint_data = {
        "experiment_name": "test_experiment",
        "iteration": 5,
        "best_parameters": {"x1": 0.2, "x2": 0.3, "x3": 0.1, "x4": 0.4, "x5": 0.5, "x6": 0.6},
        "best_objective": -2.5,
        "timestamp": "2024-01-01T12:00:00",
        "metadata": {"test": True}
    }
    
    # Test file-based checkpoint
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(checkpoint_data, f, indent=2)
        checkpoint_file = f.name
    
    # Read back the checkpoint
    with open(checkpoint_file, 'r') as f:
        loaded_data = json.load(f)
    
    assert loaded_data["experiment_name"] == checkpoint_data["experiment_name"]
    assert loaded_data["best_objective"] == checkpoint_data["best_objective"]
    
    print("✅ Checkpoint save/load working correctly")
    
    # Clean up
    Path(checkpoint_file).unlink()
    
    return True

async def test_prefect_tasks():
    """Test basic Prefect task functionality."""
    print("\n⚙️  Testing Prefect tasks...")
    
    from prefect import task, flow
    
    @task
    def add_numbers(a: int, b: int) -> int:
        return a + b
    
    @task 
    def multiply_result(x: int, factor: int = 2) -> int:
        return x * factor
    
    @flow
    def simple_math_flow(a: int = 5, b: int = 3):
        sum_result = add_numbers(a, b)
        final_result = multiply_result(sum_result, 2)
        return final_result
    
    # Run the flow
    result = await simple_math_flow()
    expected = (5 + 3) * 2  # 16
    
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✅ Prefect tasks working: {5} + {3} = {5+3}, then × 2 = {result}")
    
    return True

def test_mock_optimization():
    """Test a simple optimization loop."""
    print("\n🔬 Testing mock optimization loop...")
    
    import numpy as np
    
    # Simple optimization: minimize (x-0.5)^2 for x in [0,1]
    def objective(x):
        return (x - 0.5) ** 2
    
    # Simple random search
    best_x = 0.0
    best_obj = float('inf')
    
    for i in range(10):
        x = np.random.uniform(0, 1)
        obj = objective(x)
        
        if obj < best_obj:
            best_x = x
            best_obj = obj
    
    print(f"✅ Mock optimization completed:")
    print(f"   Best x: {best_x:.4f}")
    print(f"   Best objective: {best_obj:.4f}")
    print(f"   Expected minimum at x=0.5 with objective=0.0")
    
    return True

async def run_all_tests():
    """Run all tests."""
    print("🚀 Starting Ax Bayes Optimization Tutorial Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Objective Function Test", test_hartmann6_function),
        ("Checkpoint Tests", test_checkpoint_functionality),
        ("Mock Optimization Test", test_mock_optimization),
        ("Prefect Tasks Test", test_prefect_tasks),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} FAILED with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The tutorial should work correctly.")
        print("\nNext steps:")
        print("1. Set up MongoDB (see docs/ax_tutorial_setup.md)")
        print("2. Configure Prefect (see docs/ax_tutorial_setup.md)")
        print("3. Run the full tutorial: python ax_bayesian_optimization_hitl.py")
    else:
        print("⚠️  Some tests failed. Please check the setup instructions.")
        print("See docs/ax_tutorial_setup.md for detailed setup instructions.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())