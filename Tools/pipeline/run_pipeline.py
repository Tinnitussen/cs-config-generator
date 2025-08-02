"""
Main entry point for the command processing pipeline.

This script orchestrates the entire process of parsing, classifying,
and subcategorizing commands to generate the final JSON schemas
for the CSConfigGenerator application.
"""
import os
import sys
import argparse

# Ensure the pipeline steps and rules can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
sys.path.append(os.path.join(script_dir, '..', 'rules'))

from steps.step1_parse import parse_raw_commands
from steps.step2_classify_types import classify_command_types
from steps.step3_split_by_category import split_commands_by_category
from steps.step4_subcategorize import subcategorize

def main():
    """Main function to run the entire pipeline."""
    parser = argparse.ArgumentParser(description="Run the full command processing pipeline.")
    parser.add_argument(
        '--reclassify-all',
        action='store_true',
        help="If set, the script will re-classify all command types, overwriting any existing classifications."
    )
    args = parser.parse_args()

    print("Starting command processing pipeline...")

    # --- Path Definitions ---
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    tools_dir = os.path.join(repo_root, 'Tools')

    # Input data
    input_commands_file = os.path.join(tools_dir, 'data', 'all_commands-2025-30-07.txt')

    # Rules
    parsing_rules_file = os.path.join(tools_dir, 'rules', 'parsing_validation_rules.json')
    subcat_rules_file = os.path.join(tools_dir, 'pipeline', 'subcategorization_rules.json')

    # Intermediate data paths
    base_commands_json = os.path.join(tools_dir, 'data', 'commands.json')
    classified_output_dir = os.path.join(tools_dir, 'data', 'classified_commands')

    # Final output path
    schema_output_dir = os.path.join(repo_root, 'CSConfigGenerator', 'wwwroot', 'data', 'commandschema')

    print(f"Using Repository Root: {repo_root}")

    # --- Pipeline Execution ---

    # Step 1: Parse raw command data
    print("\n[Step 1/4] Parsing raw command data...")
    parse_raw_commands(input_commands_file, base_commands_json, parsing_rules_file)
    print("...Parsing step complete.")

    # Step 2: Add UI data and classify types
    print("\n[Step 2/4] Classifying command types...")
    classify_command_types(base_commands_json, args.reclassify_all)
    print("...Type classification step complete.")

    # Step 3: Split commands into player, server, shared
    print("\n[Step 3/4] Splitting commands into primary categories...")
    split_commands_by_category(base_commands_json, classified_output_dir)
    print("...Splitting step complete.")

    # Step 4: Sub-categorize into final schema files
    print("\n[Step 4/4] Sub-categorizing commands for UI schema...")
    subcategorize(classified_output_dir, schema_output_dir, subcat_rules_file)
    print("...Sub-categorization step complete.")

    print("\n✅ Pipeline finished successfully!")


if __name__ == "__main__":
    main()
