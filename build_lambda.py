import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_deployment_dir():
    """Clean the deployment directory if it exists."""
    deployment_dir = Path("lambda_deployment/package")
    if deployment_dir.exists():
        shutil.rmtree(deployment_dir)
    deployment_dir.mkdir(parents=True, exist_ok=True)
    return deployment_dir

def install_dependencies(deployment_dir):
    """Install dependencies into the deployment directory."""
    requirements_file = Path("lambda_deployment/requirements.txt")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--platform", "manylinux2014_x86_64",
        "--target", str(deployment_dir),
        "--implementation", "cp",
        "--python-version", "312",
        "--only-binary=:all:",
        "-r", str(requirements_file)
    ])

def copy_app_files(deployment_dir):
    """Copy application files to deployment directory."""
    # Copy app directory
    app_dir = Path("app")
    target_app_dir = deployment_dir / "app"
    shutil.copytree(app_dir, target_app_dir, ignore=shutil.ignore_patterns(
        '__pycache__',
        '*.pyc',
        'tests',
        'test_*'
    ))

def create_zip():
    """Create deployment zip file."""
    deployment_dir = Path("lambda_deployment/package")
    if os.path.exists("lambda_deployment/deployment_package.zip"):
        os.remove("lambda_deployment/deployment_package.zip")
    shutil.make_archive(
        "lambda_deployment/deployment_package",
        "zip",
        deployment_dir
    )

def main():
    print("Starting Lambda deployment package creation...")
    
    try:
        # Clean and create deployment directory
        print("Cleaning deployment directory...")
        deployment_dir = clean_deployment_dir()

        # Install dependencies
        print("Installing dependencies...")
        install_dependencies(deployment_dir)

        # Copy application files
        print("Copying application files...")
        copy_app_files(deployment_dir)

        # Create zip file
        print("Creating deployment package...")
        create_zip()

        print("Deployment package created successfully!")
        print("Location: lambda_deployment/deployment_package.zip")
        print(f"Package size: {os.path.getsize('lambda_deployment/deployment_package.zip') / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"Error creating deployment package: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()