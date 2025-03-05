
#!/usr/bin/env python3
"""
Natural Language Workflow CLI Tool

A command-line interface for converting natural language workflow descriptions
to URFN registry entries.
"""

import argparse
import json
import os
import sys
from typing import Optional, Dict, Any

from nl_to_urfn import convert_natural_language_to_urfn

def main():
    parser = argparse.ArgumentParser(
        description="Convert natural language workflow descriptions to URFN registry entries"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file", 
        help="Path to a text file containing the workflow description"
    )
    input_group.add_argument(
        "-d", "--description", 
        help="Direct workflow description as text"
    )
    input_group.add_argument(
        "--interactive", 
        action="store_true", 
        help="Interactive mode to enter description"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output", 
        help="Output file for the URFN registry JSON (default: stdout)"
    )
    parser.add_argument(
        "--registry", 
        help="Path to existing registry file to update with new entries"
    )
    parser.add_argument(
        "--pretty", 
        action="store_true", 
        help="Pretty-print the JSON output"
    )
    
    # Other options
    parser.add_argument(
        "--visualize", 
        action="store_true", 
        help="Generate a visualization of the workflow"
    )
    parser.add_argument(
        "--explain", 
        action="store_true", 
        help="Include explanation of the parsing process"
    )
    
    args = parser.parse_args()
    
    # Get workflow description from appropriate source
    description = get_workflow_description(args)
    if not description:
        parser.print_help()
        sys.exit(1)
    
    # Convert the description
    try:
        if args.explain:
            print("Processing workflow description...", file=sys.stderr)
        
        urfn_registry = convert_natural_language_to_urfn(description)
        
        if args.explain:
            workflow_name = None
            for urfn_name in urfn_registry:
                if urfn_name.startswith("urfn_workflow_"):
                    workflow_name = urfn_registry[urfn_name]["description"].replace("Workflow: ", "")
                    break
            
            print(f"✓ Successfully parsed workflow: {workflow_name}", file=sys.stderr)
            print(f"✓ Generated {len(urfn_registry)} URFN registry entries", file=sys.stderr)
        
        # Update existing registry if specified
        if args.registry and os.path.exists(args.registry):
            try:
                with open(args.registry, 'r') as f:
                    existing_registry = json.load(f)
                
                # Merge registries
                existing_registry.update(urfn_registry)
                urfn_registry = existing_registry
                
                if args.explain:
                    print(f"✓ Updated existing registry with new entries", file=sys.stderr)
            except Exception as e:
                print(f"Error updating registry file: {e}", file=sys.stderr)
        
        # Output the result
        output_registry(urfn_registry, args)
        
        # Generate visualization if requested
        if args.visualize:
            visualize_workflow(urfn_registry)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def get_workflow_description(args) -> Optional[str]:
    """
    Get the workflow description from the specified source
    
    Args:
        args: Command-line arguments
        
    Returns:
        Workflow description or None if unavailable
    """
    if args.file:
        try:
            with open(args.file, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return None
    
    elif args.description:
        return args.description
    
    elif args.interactive:
        print("Enter your workflow description (press Ctrl+D on a new line when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        return "\n".join(lines)
    
    return None

def output_registry(urfn_registry: Dict[str, Any], args):
    """
    Output the URFN registry to the specified destination
    
    Args:
        urfn_registry: Generated URFN registry entries
        args: Command-line arguments
    """
    indent = 2 if args.pretty else None
    json_output = json.dumps(urfn_registry, indent=indent)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(json_output)
            if args.explain:
                print(f"✓ Output written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
    else:
        print(json_output)

def visualize_workflow(urfn_registry: Dict[str, Any]):
    """
    Generate a visualization of the workflow
    
    Args:
        urfn_registry: URFN registry entries
    """
    try:
        # Find the workflow definition
        workflow_def = None
        for urfn_name, urfn_info in urfn_registry.items():
            if urfn_name.startswith("urfn_workflow_"):
                workflow_json = urfn_info["parameters"].get("workflow_def", "{}")
                workflow_def = json.loads(workflow_json)
                break
        
        if not workflow_def:
            print("No workflow definition found for visualization", file=sys.stderr)
            return
        
        # Generate simple ASCII visualization
        print("\nWorkflow Visualization:", file=sys.stderr)
        print(f"Name: {workflow_def.get('name', 'Unnamed Workflow')}", file=sys.stderr)
        print("Steps:", file=sys.stderr)
        
        for i, step in enumerate(workflow_def.get("steps", [])):
            step_id = step.get("id", f"step_{i}")
            step_type = step.get("type", "unknown")
            step_desc = step.get("description", "No description")
            
            print(f"  {i+1}. [{step_type}] {step_id}: {step_desc}", file=sys.stderr)
        
        print("Connections:", file=sys.stderr)
        for conn in workflow_def.get("connections", []):
            from_step = conn.get("from", "?")
            to_step = conn.get("to", "?")
            conn_type = conn.get("type", "sequence")
            
            if conn_type == "sequence":
                arrow = "-->"
            elif conn_type == "condition_true":
                arrow = "==>"
            elif conn_type == "condition_false":
                arrow = "=/>"
            else:
                arrow = "---"
            
            print(f"  {from_step} {arrow} {to_step}", file=sys.stderr)
    
    except Exception as e:
        print(f"Error generating visualization: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
