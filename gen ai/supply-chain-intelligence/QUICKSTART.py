#!/usr/bin/env python
"""
QUICK START GUIDE
Supply Chain Exception Intelligence Assistant

This guide walks you through starting the application in 3 simple steps.
"""

import subprocess
import sys
import os

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   Supply Chain Exception Intelligence Assistant                 ║
║   Quick Start Guide                                              ║
║   Detect. Prioritize. Explain. Act.                              ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def step1_install():
    print("\n" + "="*60)
    print("STEP 1: Install Dependencies")
    print("="*60)
    print("\nCommand: pip install -r requirements.txt")
    print("\nThis installs:")
    print("  - pandas (data processing)")
    print("  - scikit-learn (machine learning)")
    print("  - streamlit (dashboard)")
    print("  - plotly (charts)")
    print("  - And other dependencies...")
    
    response = input("\nDo you want to install now? (yes/no): ").strip().lower()
    if response == 'yes':
        print("\nInstalling...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✅ Installation complete!")
        return True
    return False

def step2_data():
    print("\n" + "="*60)
    print("STEP 2: Generate Dataset")
    print("="*60)
    print("\nThe project includes a script to generate sample data.")
    print("Command: python generate_dataset.py")
    print("\nThis will create:")
    print("  - data/supply_chain_data.csv")
    print("  - 2,500 realistic supply chain records")
    print("  - Includes normal and exceptional cases")
    
    if os.path.exists("data/supply_chain_data.csv"):
        print("\n✅ Dataset already exists!")
        return True
    
    response = input("\nDo you want to generate the dataset now? (yes/no): ").strip().lower()
    if response == 'yes':
        print("\nGenerating...")
        subprocess.run([sys.executable, "generate_dataset.py"])
        print("\n✅ Dataset created!")
        return True
    return False

def step3_run():
    print("\n" + "="*60)
    print("STEP 3: Run the Application")
    print("="*60)
    print("\nCommand: streamlit run app.py")
    print("\nThis will:")
    print("  - Start a local web server")
    print("  - Open the dashboard in your browser")
    print("  - Load and analyze the data")
    print("  - Display 8 interactive pages")
    print("\nBrowser: http://localhost:8501")
    
    response = input("\nDo you want to start now? (yes/no): ").strip().lower()
    if response == 'yes':
        print("\nStarting Streamlit app...")
        print("(Press Ctrl+C in the terminal to stop)\n")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        return True
    return False

def main():
    print_banner()
    
    print("\nYou're about to run the Supply Chain Intelligence Assistant!")
    print("This guide will help you get started in 3 steps.\n")
    
    # Step 1
    if not step1_install():
        print("\nSkipped Step 1. You can install manually later:")
        print("  pip install -r requirements.txt")
    
    # Step 2
    if not step2_data():
        print("\nSkipped Step 2. You can generate data manually:")
        print("  python generate_dataset.py")
    
    # Step 3
    if not step3_run():
        print("\nSkipped Step 3. You can run manually:")
        print("  streamlit run app.py")
        print("\nBrowser: http://localhost:8501")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nFor more information, see:")
    print("  - README.md (comprehensive documentation)")
    print("  - IMPLEMENTATION_SUMMARY.md (project overview)")
    print("\nFeatures:")
    print("  📊 Overview - KPIs and metrics")
    print("  🚨 Exceptions - Detailed exception analysis")
    print("  🚛 Shipments - Individual shipment review")
    print("  📦 Inventory - Stock level management")
    print("  🏭 Suppliers - Supplier performance")
    print("  🗺️ Map - Route visualization")
    print("  🤖 AI Assistant - Natural language questions")
    print("  📈 Analytics - Advanced analytics")
    print("\nHave questions? Check the README.md for detailed help!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Check that Python 3.8+ is installed: python --version")
        print("3. Verify internet connection for pip install")
        print("4. Read README.md for more help")
        sys.exit(1)
