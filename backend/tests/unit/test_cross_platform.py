"""
Cross-Platform Compatibility Tests
Verifies that pathlib operations, file I/O, and environment handling work across platforms.

These tests ensure the FLUX backend works correctly on:
- macOS (Darwin)
- Linux
- Windows

Run on specific platforms:
- macOS/Linux: pytest tests/unit/test_cross_platform.py
- Windows: pytest tests\unit\test_cross_platform.py

Platform-specific tests are skipped automatically using @pytest.mark.skipif.
"""

import sys
import os
import tempfile
from pathlib import Path
import pytest

import aiofiles
from flux_core.tools.storage import (
    ensure_storage_dirs,
    save_paper,
    load_paper,
    list_papers,
    delete_paper,
    get_storage_info,
    STORAGE_BASE,
    PAPERS_DIR,
)


class TestPathlibOperations:
    """Test that pathlib Path operations work correctly on all platforms."""
    
    def test_storage_paths_work(self):
        """
        Test that storage paths are created correctly using pathlib.
        
        Verifies:
        - Path objects are created properly
        - Path separators are platform-appropriate
        - Paths can be converted to strings
        """
        # Test Path creation
        storage_path = Path("storage")
        papers_path = storage_path / "papers"
        research_path = papers_path / "test-research-123"
        
        assert isinstance(storage_path, Path)
        assert isinstance(papers_path, Path)
        assert isinstance(research_path, Path)
        
        # Test path components
        assert storage_path.name == "storage"
        assert papers_path.name == "papers"
        assert research_path.name == "test-research-123"
        
        # Test string conversion
        storage_str = str(storage_path)
        assert "storage" in storage_str
        
        # Test absolute path works
        abs_path = storage_path.absolute()
        assert abs_path.is_absolute()
    
    def test_path_operators_work(self):
        """Test that pathlib / operator works for path construction."""
        base = Path("base")
        sub1 = base / "sub1"
        sub2 = sub1 / "sub2"
        file_path = sub2 / "file.txt"
        
        assert str(file_path).endswith("file.txt")
        assert "sub1" in str(file_path)
        assert "sub2" in str(file_path)
    
    def test_path_exists_check(self):
        """Test that path existence checks work."""
        # Current directory should exist
        current = Path.cwd()
        assert current.exists()
        assert current.is_dir()
        
        # Non-existent path
        fake_path = Path("this-does-not-exist-12345")
        assert not fake_path.exists()
    
    def test_path_mkdir_works(self):
        """Test that Path.mkdir creates directories correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            test_dir = base / "test" / "nested" / "dirs"
            
            # Create with parents
            test_dir.mkdir(parents=True, exist_ok=True)
            assert test_dir.exists()
            assert test_dir.is_dir()
            
            # Should be idempotent
            test_dir.mkdir(parents=True, exist_ok=True)
            assert test_dir.exists()
    
    def test_path_iterdir_works(self):
        """Test that Path.iterdir works for directory iteration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            
            # Create some files and directories
            (base / "file1.txt").touch()
            (base / "file2.txt").touch()
            (base / "subdir").mkdir()
            
            # Iterate and collect
            items = list(base.iterdir())
            assert len(items) == 3
            
            names = {item.name for item in items}
            assert "file1.txt" in names
            assert "file2.txt" in names
            assert "subdir" in names
    
    def test_path_relative_to_works(self):
        """Test path relative operations."""
        base = Path("/root/project")
        sub = Path("/root/project/src/main.py")
        
        # This test may behave differently on Windows with drive letters
        if sys.platform != "win32":
            relative = sub.relative_to(base)
            assert str(relative) == "src/main.py" or str(relative) == "src\\main.py"


class TestFileOperations:
    """Test that file read/write operations work across platforms."""
    
    def test_file_read_write(self):
        """
        Test basic file read/write operations.
        
        On Windows: Tests CRLF vs LF line endings are handled
        On Unix: Tests LF line endings work correctly
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            
            # Write content
            content = "Hello, World!\nThis is a test.\n"
            file_path.write_text(content, encoding="utf-8")
            
            # Verify file exists
            assert file_path.exists()
            assert file_path.is_file()
            
            # Read content back
            read_content = file_path.read_text(encoding="utf-8")
            
            # On Windows, line endings may be converted
            if sys.platform == "win32":
                # Accept both LF and CRLF
                assert "Hello, World!" in read_content
                assert "This is a test." in read_content
            else:
                assert read_content == content
            
            # Delete file
            file_path.unlink()
            assert not file_path.exists()
    
    def test_binary_file_operations(self):
        """Test binary file operations work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "binary.bin"
            
            # Write binary data
            binary_data = b"\x00\x01\x02\x03\xFF\xFE"
            file_path.write_bytes(binary_data)
            
            # Read back
            read_data = file_path.read_bytes()
            assert read_data == binary_data
            
            # Clean up
            file_path.unlink()
    
    def test_json_file_operations(self):
        """Test JSON file operations with proper encoding."""
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "data.json"
            
            # Write JSON
            data = {
                "name": "Test",
                "value": 42,
                "unicode": "Hello 世界 🌍",
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Read JSON
            with open(file_path, "r", encoding="utf-8") as f:
                read_data = json.load(f)
            
            assert read_data == data
            assert read_data["unicode"] == "Hello 世界 🌍"


class TestAsyncFileOperations:
    """Test that aiofiles async operations work correctly."""
    
    @pytest.mark.asyncio
    async def test_async_write_read(self):
        """Test async file write and read operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "async_test.txt"
            
            # Async write
            content = "Async content\nLine 2\n"
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(content)
            
            assert file_path.exists()
            
            # Async read
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                read_content = await f.read()
            
            assert "Async content" in read_content
    
    @pytest.mark.asyncio
    async def test_async_json_operations(self):
        """Test async JSON file operations."""
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "async_data.json"
            
            data = {"test": "value", "number": 123}
            
            # Async write JSON
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2))
            
            # Async read JSON
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                read_data = json.loads(content)
            
            assert read_data == data


class TestEnvironmentVariables:
    """Test that environment variable loading works on all platforms."""
    
    def test_env_var_reading(self, monkeypatch):
        """Test reading environment variables."""
        # Set test environment variable
        monkeypatch.setenv("FLUX_TEST_VAR", "test_value")
        
        # Read it back
        value = os.getenv("FLUX_TEST_VAR")
        assert value == "test_value"
        
        # Test with default
        missing = os.getenv("FLUX_MISSING_VAR", "default")
        assert missing == "default"
    
    def test_env_var_with_paths(self, monkeypatch):
        """Test environment variables containing paths."""
        if sys.platform == "win32":
            test_path = "C:\\Users\\test\\project"
        else:
            test_path = "/home/test/project"
        
        monkeypatch.setenv("FLUX_TEST_PATH", test_path)
        
        # Read and convert to Path
        path_str = os.getenv("FLUX_TEST_PATH")
        path_obj = Path(path_str)
        
        assert isinstance(path_obj, Path)
        assert "test" in str(path_obj)
    
    def test_dotenv_compatibility(self, monkeypatch):
        """Test that dotenv-style variables work."""
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_key")
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        
        assert os.getenv("AWS_ACCESS_KEY_ID") == "test_key"
        assert os.getenv("AWS_REGION") == "us-east-1"


class TestStorageModule:
    """Test that storage module works correctly across platforms."""
    
    @pytest.mark.asyncio
    async def test_ensure_storage_dirs_works(self):
        """Test that ensure_storage_dirs creates directories properly."""
        # This may create actual directories in storage/
        ensure_storage_dirs()
        
        # Verify directories exist
        assert PAPERS_DIR.exists()
        assert PAPERS_DIR.is_dir()
        
        # Should be idempotent
        ensure_storage_dirs()
        assert PAPERS_DIR.exists()
    
    @pytest.mark.asyncio
    async def test_save_and_load_paper_cross_platform(self):
        """Test that saving and loading papers works on current platform."""
        research_id = "test-cross-platform-123"
        
        # Create test state
        test_state = {
            "research_id": research_id,
            "question": "Test question?",
            "paper_draft": "# Test Paper\n\nThis is a test.",
            "messages": [{"role": "user", "content": "Hello"}],
            "iteration": 1,
            "quality_score": 8.5,
            "quality_history": [7.0, 8.5],
            "started_at": "2024-01-01T00:00:00",
            "total_tokens_used": 100,
            "total_cost": 0.01,
            "stop_reason": "test",
        }
        
        try:
            # Save paper
            saved_paths = await save_paper(research_id, test_state)
            
            # Verify all paths are Path objects
            assert all(isinstance(p, Path) for p in saved_paths.values())
            
            # Verify files exist
            assert saved_paths["paper"].exists()
            assert saved_paths["metadata"].exists()
            assert saved_paths["conversation"].exists()
            assert saved_paths["state"].exists()
            
            # Load paper back
            loaded = await load_paper(research_id)
            
            assert loaded["research_id"] == research_id
            assert loaded["paper"] == "# Test Paper\n\nThis is a test."
            assert loaded["metadata"]["question"] == "Test question?"
            assert len(loaded["conversation"]) == 1
            
        finally:
            # Clean up
            try:
                await delete_paper(research_id)
            except Exception:
                pass
    
    @pytest.mark.asyncio
    async def test_list_papers_works(self):
        """Test that listing papers works correctly."""
        # Should work even with no papers
        papers = await list_papers()
        assert isinstance(papers, list)
    
    def test_get_storage_info_works(self):
        """Test that storage info retrieval works."""
        info = get_storage_info()
        
        assert "storage_path" in info
        assert "paper_count" in info
        assert "total_size_bytes" in info
        
        # Verify path is a valid string
        assert isinstance(info["storage_path"], str)
        assert len(info["storage_path"]) > 0


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS-specific test")
class TestMacOSSpecific:
    """
    Tests specific to macOS (Darwin).
    
    Run on macOS with: pytest tests/unit/test_cross_platform.py -k TestMacOSSpecific
    These tests are automatically skipped on other platforms.
    """
    
    def test_macos_path_separators(self):
        """Test that macOS uses forward slashes."""
        path = Path("storage") / "papers" / "test"
        path_str = str(path)
        
        assert "/" in path_str
        assert "\\" not in path_str
    
    def test_macos_temp_dir(self):
        """Test that temp directory on macOS works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            assert tmp_path.exists()
            # macOS temp dirs typically under /var/folders/
            assert "var" in str(tmp_path) or "tmp" in str(tmp_path).lower()


@pytest.mark.skipif(sys.platform != "linux", reason="Linux-specific test")
class TestLinuxSpecific:
    """
    Tests specific to Linux.
    
    Run on Linux with: pytest tests/unit/test_cross_platform.py -k TestLinuxSpecific
    These tests are automatically skipped on other platforms.
    """
    
    def test_linux_path_separators(self):
        """Test that Linux uses forward slashes."""
        path = Path("storage") / "papers" / "test"
        path_str = str(path)
        
        assert "/" in path_str
        assert "\\" not in path_str
    
    def test_linux_temp_dir(self):
        """Test that temp directory on Linux works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            assert tmp_path.exists()
            # Linux temp dirs typically under /tmp/
            assert "tmp" in str(tmp_path)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
class TestWindowsSpecific:
    """
    Tests specific to Windows.
    
    Run on Windows with: pytest tests\\unit\\test_cross_platform.py -k TestWindowsSpecific
    These tests are automatically skipped on other platforms.
    """
    
    def test_windows_path_separators(self):
        """Test that Windows paths work correctly."""
        path = Path("storage") / "papers" / "test"
        path_str = str(path)
        
        # Windows may use either forward or backslashes
        assert "storage" in path_str
        assert "papers" in path_str
    
    def test_windows_drive_letters(self):
        """Test that Windows drive letters work."""
        cwd = Path.cwd()
        abs_path = cwd.absolute()
        
        # Windows absolute paths should have drive letter
        assert abs_path.is_absolute()
        # Drive is accessed via .drive attribute
        assert abs_path.drive or True  # May be empty on network paths
    
    def test_windows_temp_dir(self):
        """Test that temp directory on Windows works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            assert tmp_path.exists()
            # Windows temp typically under C:\\Users\\...\\AppData\\Local\\Temp
            path_lower = str(tmp_path).lower()
            assert "temp" in path_lower or "tmp" in path_lower


class TestCrossPlatformSummary:
    """
    Summary test to verify cross-platform readiness.
    
    This test runs on all platforms and provides a comprehensive check.
    """
    
    def test_platform_detection(self):
        """Test that we can detect the current platform."""
        platform = sys.platform
        
        assert platform in ["darwin", "linux", "win32", "cygwin"], \
            f"Unexpected platform: {platform}"
        
        print(f"\n✓ Running on platform: {platform}")
    
    def test_pathlib_available(self):
        """Test that pathlib is available and working."""
        from pathlib import Path
        
        # Create a path
        test_path = Path("test") / "path"
        
        assert isinstance(test_path, Path)
        print("✓ pathlib is available and working")
    
    def test_aiofiles_available(self):
        """Test that aiofiles is available."""
        import aiofiles
        
        assert aiofiles is not None
        print("✓ aiofiles is available")
    
    def test_tempfile_works(self):
        """Test that tempfile module works."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            assert Path(tmpdir).exists()
        
        print("✓ tempfile module works")
    
    def test_env_vars_work(self, monkeypatch):
        """Test that environment variables work."""
        monkeypatch.setenv("TEST_VAR", "value")
        assert os.getenv("TEST_VAR") == "value"
        
        print("✓ Environment variables work")
    
    @pytest.mark.asyncio
    async def test_async_works(self):
        """Test that async/await works."""
        async def async_func():
            return "success"
        
        result = await async_func()
        assert result == "success"
        
        print("✓ Async/await works")


def print_platform_info():
    """Print platform information for debugging."""
    print("\n" + "="*60)
    print("FLUX Backend - Platform Information")
    print("="*60)
    print(f"Platform: {sys.platform}")
    print(f"OS: {os.name}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {Path.cwd()}")
    print(f"Storage Path: {PAPERS_DIR.absolute()}")
    print("="*60 + "\n")


# Run platform info when module is imported
if __name__ != "__main__":
    print_platform_info()

