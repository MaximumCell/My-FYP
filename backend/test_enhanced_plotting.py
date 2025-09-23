#!/usr/bin/env python3
"""
Test script for enhanced plotting functionality
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from simulation.plot_2d import plot_equation_2d, plot_from_csv_columns
from simulation.plot_3d import plot_surface, plot_from_csv_xyz
from simulation.run_simulation import run_simulation

def test_2d_equation_plotting():
    """Test 2D equation plotting with customization"""
    print("Testing 2D equation plotting...")
    
    data = {
        'mode': 'equation',
        'equation': 'sin(x)',
        'x_min': -6.28,
        'x_max': 6.28,
        'resolution': 500,
        'width': 1200,
        'height': 800,
        'dpi': 300,
        'title': 'Test Sine Wave',
        'xlabel': 'x values',
        'ylabel': 'sin(x)',
        'line_color': '#ff6b6b',
        'background_color': '#ffffff',
        'grid': 'true',
        'style': 'seaborn'
    }
    
    result = run_simulation(data, host_url='http://localhost:5000')
    print(f"2D Equation Result: {result}")
    return 'html_url' in result and 'error' not in result

def test_3d_surface_plotting():
    """Test 3D surface plotting with customization"""
    print("Testing 3D surface plotting...")
    
    data = {
        'mode': '3d_surface',
        'equation': 'sin(x)*cos(y)',
        'x_min': -5,
        'x_max': 5,
        'y_min': -5,
        'y_max': 5,
        'resolution': 50,
        'width': 1200,
        'height': 800,
        'title': 'Test 3D Surface',
        'xlabel': 'X axis',
        'ylabel': 'Y axis',
        'zlabel': 'Z axis',
        'colormap': 'plasma',
        'background_color': '#ffffff',
        'grid': 'true'
    }
    
    result = run_simulation(data, host_url='http://localhost:5000')
    print(f"3D Surface Result: {result}")
    return 'html_url' in result and 'error' not in result

def test_csv_2d_plotting():
    """Test CSV 2D plotting functionality"""
    print("Testing CSV 2D plotting...")
    
    # Create sample CSV data
    import tempfile
    import io
    
    csv_content = """x,y,z
1,2,3
2,4,6
3,6,9
4,8,12
5,10,15"""
    
    # Simulate file upload
    csv_file = io.StringIO(csv_content)
    csv_file.name = 'test.csv'
    
    # Create a mock file object
    class MockFile:
        def __init__(self, content):
            self.content = content
            self.position = 0
        
        def read(self):
            return self.content
        
        def seek(self, position):
            self.position = position
    
    mock_file = MockFile(csv_content)
    files = {'file': mock_file}
    
    data = {
        'mode': 'csv',
        'x_col': 'x',
        'y_col': 'y',
        'width': 1200,
        'height': 800,
        'title': 'Test CSV Plot',
        'xlabel': 'X values',
        'ylabel': 'Y values',
        'line_color': '#4ecdc4',
        'marker_style': 'o',
        'grid': 'true'
    }
    
    result = run_simulation(data, files=files, host_url='http://localhost:5000')
    print(f"CSV 2D Result: {result}")
    return 'html_url' in result and 'error' not in result

def test_csv_3d_plotting():
    """Test CSV 3D plotting functionality"""
    print("Testing CSV 3D plotting...")
    
    csv_content = """x,y,z
1,1,2
1,2,3
1,3,4
2,1,3
2,2,4
2,3,5
3,1,4
3,2,5
3,3,6"""
    
    class MockFile:
        def __init__(self, content):
            self.content = content
            self.position = 0
        
        def read(self):
            return self.content
        
        def seek(self, position):
            self.position = position
    
    mock_file = MockFile(csv_content)
    files = {'file': mock_file}
    
    data = {
        'mode': 'csv',
        'x_col': 'x',
        'y_col': 'y',
        'z_col': 'z',
        'width': 1200,
        'height': 800,
        'title': 'Test CSV 3D Plot',
        'xlabel': 'X values',
        'ylabel': 'Y values',
        'zlabel': 'Z values',
        'colormap': 'viridis',
        'marker_style': 'circle',
        'grid': 'true'
    }
    
    result = run_simulation(data, files=files, host_url='http://localhost:5000')
    print(f"CSV 3D Result: {result}")
    return 'html_url' in result and 'error' not in result

if __name__ == '__main__':
    print("Starting enhanced plotting tests...\n")
    
    tests = [
        ("2D Equation Plotting", test_2d_equation_plotting),
        ("3D Surface Plotting", test_3d_surface_plotting),
        ("CSV 2D Plotting", test_csv_2d_plotting),
        ("CSV 3D Plotting", test_csv_3d_plotting),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"✅ {test_name}: {'PASSED' if success else 'FAILED'}\n")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name}: FAILED with error: {e}\n")
    
    print("=" * 50)
    print("TEST SUMMARY:")
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")