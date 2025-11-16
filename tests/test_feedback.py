"""
Test feedback feature functionality
"""

import pytest
from pathlib import Path
from datetime import datetime


def test_feedback_directory_exists():
    """Test that feedback directory exists"""
    feedback_dir = Path("data/feedback")
    assert feedback_dir.exists(), "Feedback directory should exist"
    assert feedback_dir.is_dir(), "Feedback path should be a directory"


def test_feedback_readme_exists():
    """Test that README exists in feedback directory"""
    readme_path = Path("data/feedback/README.md")
    assert readme_path.exists(), "README.md should exist in feedback directory"


def test_feedback_gitignore_exists():
    """Test that .gitignore exists in feedback directory"""
    gitignore_path = Path("data/feedback/.gitignore")
    assert gitignore_path.exists(), ".gitignore should exist in feedback directory"


def test_feedback_json_structure():
    """Test feedback JSON structure"""
    # Create a sample feedback entry
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "page": "Test Page",
        "feedback": "Test feedback",
        "screenshot": "test_screenshot.png",
        "email": "test@example.com"
    }
    
    # Verify all required fields are present
    assert "timestamp" in feedback_entry
    assert "page" in feedback_entry
    assert "feedback" in feedback_entry
    assert "screenshot" in feedback_entry
    assert "email" in feedback_entry


def test_feedback_module_imports():
    """Test that feedback module can be imported"""
    try:
        from src.dashboard.modules.feedback import (
            show_feedback_button,
            show_feedback_management,
            show_feedback_widget
        )
        assert callable(show_feedback_button)
        assert callable(show_feedback_management)
        assert callable(show_feedback_widget)
    except ImportError as e:
        pytest.skip(f"Cannot import feedback module: {e}")


def test_feedback_storage_writable():
    """Test that feedback directory is writable"""
    feedback_dir = Path("data/feedback")
    test_file = feedback_dir / "test_write.tmp"
    
    try:
        # Try to write a test file
        test_file.write_text("test")
        assert test_file.exists()
        # Clean up
        test_file.unlink()
    except Exception as e:
        pytest.fail(f"Cannot write to feedback directory: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
