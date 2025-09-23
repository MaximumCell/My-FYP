#!/usr/bin/env python3
"""
Test script to verify CSV upload functionality for both 2D and 3D plots
"""
import requests
import os

# Test CSV data
csv_data = """x,y,z
1,2,3
2,4,6
3,6,9
4,8,12
5,10,15
"""

def test_2d_plot_csv():
    """Test 2D CSV plotting endpoint"""
    print("Testing 2D CSV plot endpoint...")
    
    # Create a temporary CSV file
    with open('/tmp/test_2d.csv', 'w') as f:
        f.write(csv_data)
    
    # Test /simulation/plot_csv endpoint
    with open('/tmp/test_2d.csv', 'rb') as f:
        files = {'file': f}
        data = {
            'x_col': 'x',
            'y_col': 'y',
            'format': 'html',
            'width': '800',
            'height': '600'
        }
        try:
            response = requests.post('http://localhost:5000/simulation/plot_csv', files=files, data=data)
            print(f"2D CSV Response Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✓ 2D CSV endpoint working!")
                print(f"  HTML URL: {result.get('html_url', 'N/A')}")
            else:
                print(f"✗ 2D CSV endpoint failed: {response.text}")
        except Exception as e:
            print(f"✗ 2D CSV test error: {e}")

def test_3d_plot_csv():
    """Test 3D CSV plotting endpoint"""
    print("Testing 3D CSV plot endpoint...")
    
    # Create a temporary CSV file
    with open('/tmp/test_3d.csv', 'w') as f:
        f.write(csv_data)
    
    # Test /simulation/plot3d endpoint with CSV upload
    with open('/tmp/test_3d.csv', 'rb') as f:
        files = {'file': f}
        data = {
            'x_col': 'x',
            'y_col': 'y',
            'z_col': 'z',
            'format': 'html',
            'width': '800',
            'height': '600'
        }
        try:
            response = requests.post('http://localhost:5000/simulation/plot3d', files=files, data=data)
            print(f"3D CSV Response Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✓ 3D CSV endpoint working!")
                print(f"  HTML URL: {result.get('html_url', 'N/A')}")
            else:
                print(f"✗ 3D CSV endpoint failed: {response.text}")
        except Exception as e:
            print(f"✗ 3D CSV test error: {e}")

def test_3d_plot_equation():
    """Test 3D equation plotting endpoint"""
    print("Testing 3D equation plot endpoint...")
    
    data = {
        'mode': 'equation',
        'equation': 'sin(sqrt(x**2 + y**2))',
        'x_min': -5,
        'x_max': 5,
        'y_min': -5,
        'y_max': 5,
        'resolution': 50,
        'format': 'html'
    }
    
    try:
        response = requests.post('http://localhost:5000/simulation/plot3d', json=data)
        print(f"3D Equation Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✓ 3D Equation endpoint working!")
            print(f"  HTML path: {result.get('html_path', 'N/A')}")
        else:
            print(f"✗ 3D Equation endpoint failed: {response.text}")
    except Exception as e:
        print(f"✗ 3D Equation test error: {e}")

if __name__ == "__main__":
    print("Testing CSV upload functionality...\n")
    
    # Test all endpoints
    test_2d_plot_csv()
    print()
    test_3d_plot_csv()
    print()
    test_3d_plot_equation()
    print()
    print("Tests completed!")
    
    # Cleanup
    for file in ['/tmp/test_2d.csv', '/tmp/test_3d.csv']:
        if os.path.exists(file):
            os.remove(file)