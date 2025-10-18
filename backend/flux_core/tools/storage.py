"""
Storage Module for Research Papers
Uses pathlib for cross-platform compatibility and aiofiles for async operations.
"""

import json
from pathlib import Path
from typing import Any
from datetime import datetime

import aiofiles
from loguru import logger


class StorageError(Exception):
    """Custom exception for storage errors."""
    pass


# Base storage directory using pathlib for cross-platform paths
STORAGE_BASE = Path("storage")
PAPERS_DIR = STORAGE_BASE / "papers"


def ensure_storage_dirs() -> None:
    """
    Ensure storage directories exist using pathlib.
    
    Creates directories with platform-independent paths.
    Safe to call multiple times (idempotent).
    """
    try:
        # Create storage directories with parents
        PAPERS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directories ensured at: {PAPERS_DIR.absolute()}")
    except Exception as e:
        error_msg = f"Failed to create storage directories: {e}"
        logger.error(error_msg)
        raise StorageError(error_msg) from e


async def save_paper(research_id: str, state: dict[str, Any]) -> dict[str, Path]:
    """
    Save research paper and associated data.
    
    Creates platform-independent directory structure and saves:
    - paper.md: The final paper content
    - metadata.json: Question, timing, quality scores
    - conversation.json: Full message history
    - state.json: Complete final state
    
    Args:
        research_id: Unique identifier for the research
        state: Complete research state dictionary
    
    Returns:
        Dictionary mapping file types to their Path objects
    
    Raises:
        StorageError: If save operations fail
    """
    try:
        # Ensure base directories exist
        ensure_storage_dirs()
        
        # Create research-specific directory using pathlib
        research_dir = PAPERS_DIR / research_id
        research_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving research {research_id} to {research_dir.absolute()}")
        
        # Prepare file paths using pathlib
        paper_path = research_dir / "paper.md"
        metadata_path = research_dir / "metadata.json"
        conversation_path = research_dir / "conversation.json"
        state_path = research_dir / "state.json"
        
        # Extract data from state
        paper_content = state.get("paper_draft", "")
        messages = state.get("messages", [])
        
        # Create metadata
        metadata = {
            "research_id": research_id,
            "question": state.get("question", ""),
            "started_at": state.get("started_at"),
            "completed_at": datetime.utcnow().isoformat(),
            "total_iterations": state.get("iteration", 0),
            "final_quality_score": state.get("quality_score", 0.0),
            "quality_history": state.get("quality_history", []),
            "stop_reason": state.get("stop_reason", ""),
            "total_tokens_used": state.get("total_tokens_used", 0),
            "total_cost": state.get("total_cost", 0.0),
        }
        
        # Save paper.md using async file operations
        async with aiofiles.open(paper_path, "w", encoding="utf-8") as f:
            await f.write(paper_content)
        logger.debug(f"Saved paper to {paper_path}")
        
        # Save metadata.json
        async with aiofiles.open(metadata_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
        logger.debug(f"Saved metadata to {metadata_path}")
        
        # Save conversation.json
        async with aiofiles.open(conversation_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(messages, indent=2, ensure_ascii=False))
        logger.debug(f"Saved conversation to {conversation_path}")
        
        # Save state.json (complete state for debugging)
        async with aiofiles.open(state_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(state, indent=2, ensure_ascii=False, default=str))
        logger.debug(f"Saved state to {state_path}")
        
        logger.info(f"Successfully saved research {research_id}")
        
        return {
            "paper": paper_path,
            "metadata": metadata_path,
            "conversation": conversation_path,
            "state": state_path,
        }
    
    except Exception as e:
        error_msg = f"Failed to save research {research_id}: {e}"
        logger.error(error_msg)
        raise StorageError(error_msg) from e


async def load_paper(research_id: str) -> dict[str, Any]:
    """
    Load research paper and associated data.
    
    Args:
        research_id: Unique identifier for the research
    
    Returns:
        Dictionary containing paper content, metadata, conversation, and state
    
    Raises:
        StorageError: If load operations fail or research doesn't exist
    """
    try:
        # Build research directory path using pathlib
        research_dir = PAPERS_DIR / research_id
        
        if not research_dir.exists():
            raise StorageError(f"Research {research_id} not found")
        
        if not research_dir.is_dir():
            raise StorageError(f"Research {research_id} is not a directory")
        
        logger.info(f"Loading research {research_id} from {research_dir.absolute()}")
        
        # Define file paths using pathlib
        paper_path = research_dir / "paper.md"
        metadata_path = research_dir / "metadata.json"
        conversation_path = research_dir / "conversation.json"
        state_path = research_dir / "state.json"
        
        # Load paper content
        paper_content = ""
        if paper_path.exists():
            async with aiofiles.open(paper_path, "r", encoding="utf-8") as f:
                paper_content = await f.read()
        
        # Load metadata
        metadata = {}
        if metadata_path.exists():
            async with aiofiles.open(metadata_path, "r", encoding="utf-8") as f:
                content = await f.read()
                metadata = json.loads(content)
        
        # Load conversation
        conversation = []
        if conversation_path.exists():
            async with aiofiles.open(conversation_path, "r", encoding="utf-8") as f:
                content = await f.read()
                conversation = json.loads(content)
        
        # Load state
        state = {}
        if state_path.exists():
            async with aiofiles.open(state_path, "r", encoding="utf-8") as f:
                content = await f.read()
                state = json.loads(content)
        
        logger.info(f"Successfully loaded research {research_id}")
        
        return {
            "research_id": research_id,
            "paper": paper_content,
            "metadata": metadata,
            "conversation": conversation,
            "state": state,
        }
    
    except StorageError:
        raise
    except Exception as e:
        error_msg = f"Failed to load research {research_id}: {e}"
        logger.error(error_msg)
        raise StorageError(error_msg) from e


async def list_papers() -> list[dict[str, Any]]:
    """
    List all saved papers with their metadata.
    
    Iterates through storage directory using pathlib and returns
    metadata for all papers, sorted by completion date (most recent first).
    
    Returns:
        List of metadata dictionaries, sorted by date
    
    Raises:
        StorageError: If listing fails
    """
    try:
        # Ensure storage directories exist
        ensure_storage_dirs()
        
        logger.info(f"Listing papers from {PAPERS_DIR.absolute()}")
        
        papers = []
        
        # Iterate through research directories using pathlib
        if PAPERS_DIR.exists():
            for research_dir in PAPERS_DIR.iterdir():
                # Skip non-directories and hidden files
                if not research_dir.is_dir() or research_dir.name.startswith("."):
                    continue
                
                try:
                    # Try to load metadata
                    metadata_path = research_dir / "metadata.json"
                    
                    if metadata_path.exists():
                        async with aiofiles.open(metadata_path, "r", encoding="utf-8") as f:
                            content = await f.read()
                            metadata = json.loads(content)
                            papers.append(metadata)
                    else:
                        # If no metadata, create basic info
                        papers.append({
                            "research_id": research_dir.name,
                            "question": "Unknown",
                            "completed_at": None,
                        })
                
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {research_dir.name}: {e}")
                    continue
        
        # Sort by completion date (most recent first)
        papers.sort(
            key=lambda x: x.get("completed_at") or "",
            reverse=True
        )
        
        logger.info(f"Found {len(papers)} papers")
        return papers
    
    except Exception as e:
        error_msg = f"Failed to list papers: {e}"
        logger.error(error_msg)
        raise StorageError(error_msg) from e


async def delete_paper(research_id: str) -> bool:
    """
    Delete a research paper and all associated files.
    
    Args:
        research_id: Unique identifier for the research
    
    Returns:
        True if deletion was successful
    
    Raises:
        StorageError: If deletion fails
    """
    try:
        research_dir = PAPERS_DIR / research_id
        
        if not research_dir.exists():
            logger.warning(f"Research {research_id} does not exist")
            return False
        
        if not research_dir.is_dir():
            raise StorageError(f"Research {research_id} is not a directory")
        
        logger.info(f"Deleting research {research_id} from {research_dir.absolute()}")
        
        # Delete all files in the directory
        for file_path in research_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
                logger.debug(f"Deleted file: {file_path.name}")
        
        # Remove the directory
        research_dir.rmdir()
        
        logger.info(f"Successfully deleted research {research_id}")
        return True
    
    except Exception as e:
        error_msg = f"Failed to delete research {research_id}: {e}"
        logger.error(error_msg)
        raise StorageError(error_msg) from e


def get_storage_info() -> dict[str, Any]:
    """
    Get information about storage directory.
    
    Returns:
        Dictionary with storage path, paper count, and total size
    """
    try:
        ensure_storage_dirs()
        
        paper_count = 0
        total_size = 0
        
        if PAPERS_DIR.exists():
            for research_dir in PAPERS_DIR.iterdir():
                if research_dir.is_dir() and not research_dir.name.startswith("."):
                    paper_count += 1
                    
                    # Calculate total size
                    for file_path in research_dir.rglob("*"):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
        
        return {
            "storage_path": str(PAPERS_DIR.absolute()),
            "paper_count": paper_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
    
    except Exception as e:
        logger.error(f"Failed to get storage info: {e}")
        return {
            "storage_path": str(PAPERS_DIR.absolute()),
            "paper_count": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0.0,
            "error": str(e),
        }

