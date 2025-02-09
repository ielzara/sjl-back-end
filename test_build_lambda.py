import os
from pathlib import Path

def test_deployment_structure():
    """Test what files would be included in the deployment package."""
    print("Checking deployment structure...")
    
    # Check deployment directory
    deployment_dir = Path("lambda_deployment/package")
    print(f"\nWould create directory: {deployment_dir}")
    
    # Check requirements
    requirements_file = Path("lambda_deployment/requirements.txt")
    if requirements_file.exists():
        print(f"\nWould install dependencies from: {requirements_file}")
        with open(requirements_file) as f:
            print("Dependencies to install:")
            for line in f:
                print(f"  - {line.strip()}")
    
    # Check app files
    app_dir = Path("app")
    print(f"\nWould copy files from: {app_dir}")
    excluded = {'__pycache__', '*.pyc', 'tests', 'test_*'}
    
    def list_files(directory, indent=0):
        for item in directory.iterdir():
            if item.is_dir():
                if not any(item.match(pattern) for pattern in excluded):
                    print("  " * indent + f"📁 {item.name}/")
                    list_files(item, indent + 1)
            else:
                if not any(item.match(pattern) for pattern in excluded):
                    print("  " * indent + f"📄 {item.name}")
    
    list_files(app_dir)
    
    print(f"\nWould create: lambda_deployment/deployment_package.zip")

if __name__ == "__main__":
    test_deployment_structure()