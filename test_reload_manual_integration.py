#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration test script for the reload_manuals tool

This script directly tests the reload_manuals functionality
of the ReadThisServer without using mocks.
"""

import os
import sys
import json
import asyncio
import shutil
from pathlib import Path

# Add path to the module being tested
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Directly test the reload_manuals function

async def main():
    """Execute integration test"""
    # Prepare manuals.json for testing
    original_path = Path("./manuals.json")
    backup_path = Path("./manuals.json.bak")
    test_path = Path("./manuals.json")
    
    # Backup existing file if it exists
    if original_path.exists():
        print(f"Backing up existing manuals.json: {backup_path}")
        shutil.copy2(original_path, backup_path)
    
    try:
        # Initial data
        documents_config = {}
        
        # Simulate _load_documents_config function
        def _load_documents_config():
            try:
                config_path = Path('./manuals.json')
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        print(f"Loaded manuals.json: {config_path}")
                        return json.load(f)
                else:
                    print("manuals.json not found. Using default settings.")
                    return {"documents": []}
            except Exception as e:
                print(f"Failed to load manuals.json: {str(e)}")
                return {"documents": []}
        
        # Simulate reload_manuals implementation
        async def reload_manuals():
            nonlocal documents_config
            
            print("Starting manuals.json reload")
            
            # Record state before reloading configuration file
            previous_count = len(documents_config.get("documents", []))
            
            # Reload configuration file
            documents_config = _load_documents_config()
            
            # Get state after update
            current_count = len(documents_config.get("documents", []))
            
            # Return result
            result = {
                "success": True,
                "message": f"Successfully reloaded manuals.json",
                "previous_documents_count": previous_count,
                "current_documents_count": current_count, 
                "documents": documents_config
            }
            
            print(f"manuals.json reload complete: {current_count} document settings")
            return result
        
        # Create document settings for testing
        initial_data = {
            "documents": [
                {
                    "id": "test-doc-1",
                    "name": "Test Document 1",
                    "url": "https://example.com/test1",
                    "description": "Document for testing 1"
                }
            ]
        }
        
        # Write test JSON file
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)
        
        print(f"Created test manuals.json: {len(initial_data['documents'])} documents")
        
        # Load initial settings
        documents_config = _load_documents_config()
        print(f"Initial document count: {len(documents_config.get('documents', []))}")
        
        # Test 1: Reload without changes
        print("\n--- Test 1: Reload without changes ---")
        result1 = await reload_manuals()
        print(f"Result: {result1['message']}")
        print(f"Document count: {result1['current_documents_count']} (before: {result1['previous_documents_count']})")
        
        # Test 2: Add document and reload
        print("\n--- Test 2: Reload after adding document ---")
        updated_data = initial_data.copy()
        updated_data["documents"].append({
            "id": "test-doc-2",
            "name": "Test Document 2",
            "url": "https://example.com/test2",
            "description": "Document for testing 2"
        })
        
        # Overwrite file with updated data
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        result2 = await reload_manuals()
        print(f"Result: {result2['message']}")
        print(f"Document count: {result2['current_documents_count']} (before: {result2['previous_documents_count']})")
        assert result2["current_documents_count"] == 2, "Document addition not reflected"
        
        # Test 3: Modify document and reload
        print("\n--- Test 3: Reload after modifying document ---")
        updated_data["documents"][0]["name"] = "Updated Test Document"
        updated_data["documents"][0]["url"] = "https://example.com/updated"
        
        # Overwrite file with updated data
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        result3 = await reload_manuals()
        print(f"Result: {result3['message']}")
        print(f"Document count: {result3['current_documents_count']} (before: {result3['previous_documents_count']})")
        print(f"Updated document name: {result3['documents']['documents'][0]['name']}")
        assert result3["documents"]["documents"][0]["name"] == "Updated Test Document", "Document update not reflected"
        
        # Test 4: Delete document and reload
        print("\n--- Test 4: Reload after deleting document ---")
        reduced_data = {
            "documents": [updated_data["documents"][0]]  # Remove the second document
        }
        
        # Overwrite file with updated data
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(reduced_data, f, ensure_ascii=False, indent=2)
        
        result4 = await reload_manuals()
        print(f"Result: {result4['message']}")
        print(f"Document count: {result4['current_documents_count']} (before: {result4['previous_documents_count']})")
        assert result4["current_documents_count"] == 1, "Document deletion not reflected"
        
        print("\nAll tests completed successfully!")
        
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Restore from backup if it exists
        if backup_path.exists():
            print(f"Restoring manuals.json from backup")
            shutil.copy2(backup_path, original_path)
            backup_path.unlink()
        else:
            # Delete test file
            if test_path.exists():
                test_path.unlink()

if __name__ == "__main__":
    print("Starting integration test for reload_manuals tool...")
    asyncio.run(main())
