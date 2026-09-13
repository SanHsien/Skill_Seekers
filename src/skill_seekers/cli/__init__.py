"""Skill Seekers CLI tools package.

This package provides command-line tools for converting documentation
websites into AI skills.

Main modules:
    - doc_scraper: Main documentation scraping and skill building tool
    - llms_txt_detector: Detect llms.txt files at documentation URLs
    - llms_txt_downloader: Download llms.txt content
    - llms_txt_parser: Parse llms.txt markdown content
    - pdf_scraper: Extract documentation from PDF files
    - enhance_skill: AI-powered skill enhancement (API-based)
    - enhance_skill_local: AI-powered skill enhancement (local)
    - estimate_pages: Estimate page count before scraping
    - package_skill: Package skills into .zip files
    - upload_skill: Upload skills to target platform
    - utils: Shared utility functions
"""

try:
    from .llms_txt_detector import LlmsTxtDetector
except ImportError:
    LlmsTxtDetector = None  # type: ignore[assignment,misc]

try:
    from .llms_txt_downloader import LlmsTxtDownloader
except ImportError:
    LlmsTxtDownloader = None  # type: ignore[assignment,misc]

try:
    from .llms_txt_parser import LlmsTxtParser
except ImportError:
    LlmsTxtParser = None  # type: ignore[assignment,misc]

# ExecutionContext - single source of truth for all configuration
try:
    from .execution_context import ExecutionContext, get_context
except ImportError:
    ExecutionContext = None  # type: ignore[assignment,misc]
    get_context = None  # type: ignore[assignment]

try:
    from .utils import open_folder, read_reference_files
except ImportError:
    # utils.py might not exist in all configurations
    open_folder = None
    read_reference_files = None

# Import centralized version
from skill_seekers._version import __version__

__all__ = [
    "LlmsTxtDetector",
    "LlmsTxtDownloader",
    "LlmsTxtParser",
    "ExecutionContext",
    "get_context",
    "open_folder",
    "read_reference_files",
    "__version__",
]
