"""
Converter base class and auto-discovery registry.
Adding a new IDE = implement BaseConverter + register.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Type

from .types import CapturedFile, ConversionResult, IDEFormat


class BaseConverter(ABC):
    @property
    @abstractmethod
    def format_info(self) -> IDEFormat: ...

    @abstractmethod
    def convert(self, source_root: Path, dest_root: Path, verbose: bool = True, force: bool = False) -> ConversionResult: ...

    @abstractmethod
    def install_mcp(self, source_root: Path, dest_root: Path, force: bool = False) -> bool: ...

    @abstractmethod
    def clean(self, project_path: Path) -> bool: ...

    def reverse_convert(
        self,
        project_path: Path,
        agent_dir: Path,
        verbose: bool = True,
    ) -> List[CapturedFile]:
        """Dry-run scan: return list of capturable files. Default: no support."""
        return []

    def apply_reverse_capture(
        self,
        captured: CapturedFile,
        project_path: Path,
        agent_dir: Path,
    ) -> bool:
        """Apply reverse capture for one file. Default: not supported."""
        return False

    def build_bridge_meta_map(self, project_path: Path) -> Dict[str, str]:
        """Return {ide_relative_path: agent_relative_path} for .bridge-meta.json."""
        return {}

    @property
    def supports_capture(self) -> bool:
        """Does this converter support reverse capture?"""
        return False

    @property
    def mcp_output_path(self) -> Optional[str]:
        """Relative path for MCP config output. e.g. '.cursor/mcp.json'"""
        return None

    def transform_mcp_config(self, config: Dict) -> Dict:
        """Transform MCP config dict for this IDE format. Default: no-op."""
        return config

    @property
    def name(self) -> str:
        return self.format_info.name

    @property
    def display_name(self) -> str:
        return self.format_info.display_name

    @property
    def checkbox_label(self) -> str:
        return self.format_info.checkbox_label or f"{self.display_name} ({self.format_info.output_dir}/)"


class ConverterRegistry:
    def __init__(self):
        self._converters: Dict[str, BaseConverter] = {}

    def register(self, converter_class: Type[BaseConverter]) -> None:
        instance = converter_class()
        self._converters[instance.name] = instance

    def get(self, name: str) -> Optional[BaseConverter]:
        return self._converters.get(name.lower())

    def all(self) -> List[BaseConverter]:
        return list(self._converters.values())

    def names(self) -> List[str]:
        return list(self._converters.keys())


converter_registry = ConverterRegistry()
