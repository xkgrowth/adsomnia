"""
Documentation synchronization utility for keeping local docs in sync with Context7.
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from .everflow_api_validator import Context7Client, get_validator
import logging

logger = logging.getLogger(__name__)


class DocumentationSync:
    """Synchronizes local documentation with Context7."""
    
    def __init__(self):
        self.context7 = Context7Client()
        self.docs_dir = Path(__file__).parent.parent.parent / "docs" / "api"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    def sync_documentation(self, force: bool = False) -> Dict[str, any]:
        """
        Sync documentation from Context7 to local files.
        
        Args:
            force: Force sync even if recently synced
        
        Returns:
            Sync result dictionary
        """
        logger.info("Starting documentation sync from Context7...")
        
        docs = self.context7.get_library_docs(force_refresh=force)
        
        if not docs:
            logger.warning("Could not fetch documentation from Context7")
            return {
                "success": False,
                "message": "Could not fetch documentation from Context7",
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate updated reference documentation
        reference_doc = self._generate_reference_doc(docs)
        
        # Write to file
        reference_path = self.docs_dir / "everflow_api_reference.md"
        reference_path.write_text(reference_doc, encoding="utf-8")
        
        # Generate change report
        changes = self._detect_changes(docs)
        
        logger.info(f"Documentation synced successfully to {reference_path}")
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "reference_path": str(reference_path),
            "changes_detected": len(changes) > 0,
            "changes": changes
        }
    
    def _generate_reference_doc(self, docs: Dict[str, Any]) -> str:
        """Generate markdown reference documentation from Context7 docs."""
        lines = [
            "# Everflow API Reference",
            "",
            f"> Auto-generated from Context7 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Authentication",
            "",
            "All requests require the `X-Eflow-API-Key` header:",
            "",
            "```",
            "X-Eflow-API-Key: YOUR_API_KEY",
            "Content-Type: application/json",
            "```",
            "",
            "## Base URL",
            "",
            "```",
            "https://api.eflow.team",
            "```",
            "",
            "> **Note:** This documentation is automatically synced from Context7.",
            "> For the most up-to-date information, the system uses Context7 directly.",
            "",
            "## Endpoints",
            "",
        ]
        
        # Add endpoint documentation
        # In a full implementation, this would parse the Context7 docs structure
        # and generate comprehensive endpoint documentation
        
        validator = get_validator()
        validator.initialize()
        
        for endpoint, spec in validator.endpoint_specs.items():
            lines.extend([
                f"### {spec.method} {endpoint}",
                "",
                f"**Description:** {spec.description}",
                "",
                "**Required Parameters:**",
                ""
            ])
            
            for param in spec.required_params:
                param_type = spec.param_types.get(param, "unknown")
                lines.append(f"- `{param}` ({param_type})")
            
            if spec.optional_params:
                lines.extend([
                    "",
                    "**Optional Parameters:**",
                    ""
                ])
                for param in spec.optional_params:
                    param_type = spec.param_types.get(param, "unknown")
                    lines.append(f"- `{param}` ({param_type})")
            
            if spec.deprecated:
                lines.extend([
                    "",
                    f"> ⚠️ **Deprecated:** This endpoint is deprecated.",
                ])
                if spec.alternative:
                    lines.append(f"> Use `{spec.alternative}` instead.")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def _detect_changes(self, docs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes in API documentation."""
        changes = []
        
        # Compare with previous version
        # In a full implementation, this would compare with the last synced version
        # and detect new endpoints, deprecated endpoints, parameter changes, etc.
        
        return changes
    
    def generate_migration_guide(self, changes: List[Dict[str, Any]]) -> str:
        """Generate migration guide for API changes."""
        if not changes:
            return "No changes detected."
        
        lines = [
            "# API Migration Guide",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Changes Detected",
            "",
        ]
        
        for change in changes:
            lines.append(f"### {change.get('type', 'Unknown')}")
            lines.append(f"- **Endpoint:** {change.get('endpoint', 'N/A')}")
            lines.append(f"- **Description:** {change.get('description', 'N/A')}")
            lines.append("")
        
        return "\n".join(lines)


def sync_docs_command():
    """CLI command for syncing documentation."""
    sync = DocumentationSync()
    result = sync.sync_documentation(force=True)
    
    if result["success"]:
        print(f"✅ Documentation synced successfully")
        print(f"   Path: {result['reference_path']}")
        if result["changes_detected"]:
            print(f"   ⚠️  {len(result['changes'])} changes detected")
    else:
        print(f"❌ Documentation sync failed: {result['message']}")


if __name__ == "__main__":
    sync_docs_command()

