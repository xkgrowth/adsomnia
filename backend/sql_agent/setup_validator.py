"""
Setup script for initializing the Everflow API validator.
Run this on server startup or as a standalone script.
"""
from .everflow_api_validator import get_validator
from .docs_sync import DocumentationSync
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_validator():
    """Initialize validator and sync documentation."""
    print("🔧 Setting up Everflow API Validator...")
    
    # Initialize validator
    validator = get_validator()
    success = validator.initialize(force_refresh=True)
    
    if success:
        print("✅ Validator initialized successfully")
    else:
        print("⚠️  Validator initialized with fallback data")
    
    # Sync documentation
    print("\n📚 Syncing documentation from Context7...")
    sync = DocumentationSync()
    result = sync.sync_documentation(force=True)
    
    if result["success"]:
        print(f"✅ Documentation synced to {result['reference_path']}")
        if result["changes_detected"]:
            print(f"⚠️  {len(result['changes'])} changes detected")
    else:
        print(f"⚠️  Documentation sync failed: {result['message']}")
    
    # Validate all endpoints
    print("\n🔍 Validating all endpoints...")
    results = validator.validate_all_endpoints()
    
    valid = sum(1 for r in results.values() if r.valid)
    total = len(results)
    
    print(f"✅ {valid}/{total} endpoints validated")
    
    # Show any issues
    for endpoint, result in results.items():
        if not result.valid:
            print(f"❌ {endpoint}:")
            for error in result.errors:
                print(f"   - {error}")
        elif result.warnings:
            print(f"⚠️  {endpoint}:")
            for warning in result.warnings:
                print(f"   - {warning}")
    
    print("\n✅ Setup complete!")


if __name__ == "__main__":
    setup_validator()


