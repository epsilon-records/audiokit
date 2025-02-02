"""Setup test environment."""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create required directories
def setup():
    """Setup test environment."""
    # Create fixtures directory
    fixture_dir = Path(__file__).parent / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output directory
    output_dir = fixture_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables for testing
    os.environ["AUDIOKIT_TEST"] = "true"
    os.environ["AUDIOKIT_OUTPUT_DIR"] = str(output_dir)
    os.environ["AUDIOKIT_LOG_LEVEL"] = "DEBUG"

if __name__ == "__main__":
    setup() 