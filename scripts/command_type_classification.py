import json
import re
from typing import Dict, List, Tuple, Optional

def load_commands(filepath: str) -> List[Dict]:
    """Load the combined.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_numeric_string(value: str) -> bool:
    """Check if a string represents a number"""
    if not value:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_integer_string(value: str) -> bool:
    """Check if a string represents an integer"""
    if not value:
        return False
    try:
        val = float(value)
        return val.is_integer()
    except ValueError:
        return False

def is_boolean_string(value: str) -> bool:
    """Check if a string represents a boolean"""
    return value.lower() in ['true', 'false', '1', '0']

def analyze_command_patterns(commands: List[Dict]) -> Dict:
    """Analyze patterns in the command data to help with classification"""
    stats = {
        'total_commands': len(commands),
        'null_defaults': 0,
        'boolean_defaults': 0,
        'integer_defaults': 0,
        'float_defaults': 0,
        'string_defaults': 0,
        'common_prefixes': {},
        'flag_patterns': {}
    }
    
    for cmd in commands:
        default_val = cmd['consoleData']['defaultValue']
        flags = cmd['consoleData']['flags']
        
        if default_val is None:
            stats['null_defaults'] += 1
        elif is_boolean_string(default_val):
            stats['boolean_defaults'] += 1
        elif is_integer_string(default_val):
            stats['integer_defaults'] += 1
        elif is_numeric_string(default_val):
            stats['float_defaults'] += 1
        else:
            stats['string_defaults'] += 1
            
        # Track command prefixes
        prefix = cmd['command'].split('_')[0]
        stats['common_prefixes'][prefix] = stats['common_prefixes'].get(prefix, 0) + 1
        
        # Track flag combinations
        flag_key = ','.join(sorted(flags))
        stats['flag_patterns'][flag_key] = stats['flag_patterns'].get(flag_key, 0) + 1
    
    return stats

def classify_command_type(command: Dict) -> Tuple[str, float]:
    """
    Classify a command and return (type, confidence_score)
    Confidence score: 0.0-1.0 where 1.0 is completely certain
    """
    cmd_name = command['command']
    default_val = command['consoleData']['defaultValue']
    flags = command['consoleData']['flags']
    description = command['consoleData']['description']
    
    # Rule 1: null defaultValue usually means it's a command
    if default_val is None:
        return 'command', 0.9
    
    # Rule 2: Boolean values
    if is_boolean_string(default_val):
        return 'boolean', 0.95
    
    # Rule 3: Numeric values
    if is_numeric_string(default_val):
        if is_integer_string(default_val):
            # Check for common bitmask patterns
            if any(keyword in cmd_name.lower() for keyword in ['flag', 'mask', 'bits']):
                return 'bitmask', 0.7
            # Check for common enum patterns
            elif any(keyword in cmd_name.lower() for keyword in ['mode', 'type', 'level', 'quality']):
                return 'enum', 0.6
            else:
                return 'integer', 0.8
        else:
            return 'float', 0.9
    
    # Rule 4: String values - check for common enum patterns
    if default_val:
        # Common enum indicators in the default value
        if default_val.isdigit() and int(default_val) < 10:
            return 'enum', 0.6
        # Color values
        elif re.match(r'^[\d\s]+$', default_val) and len(default_val.split()) in [3, 4]:
            return 'string', 0.7  # Likely RGB/RGBA color
        # File paths or URLs
        elif '/' in default_val or '\\' in default_val or default_val.endswith(('.cfg', '.txt', '.wav', '.mp3')):
            return 'string', 0.8
        else:
            return 'string', 0.7
    
    # Fallback: empty string default
    return 'string', 0.5

def add_type_classification(commands: List[Dict]) -> List[Dict]:
    """Add type classification to each command"""
    classified_commands = []
    classification_stats = {
        'boolean': 0, 'integer': 0, 'float': 0, 'string': 0, 
        'enum': 0, 'command': 0, 'bitmask': 0
    }
    low_confidence = []
    
    for cmd in commands:
        cmd_type, confidence = classify_command_type(cmd)
        
        # Add the type to uiData
        cmd['uiData'] = {
            'type': cmd_type,
            'confidence': confidence
        }
        
        classification_stats[cmd_type] += 1
        
        if confidence < 0.7:
            low_confidence.append({
                'command': cmd['command'],
                'type': cmd_type,
                'confidence': confidence,
                'defaultValue': cmd['consoleData']['defaultValue']
            })
        
        classified_commands.append(cmd)
    
    return classified_commands, classification_stats, low_confidence

def save_classified_commands(commands: List[Dict], output_file: str):
    """Save the classified commands to a JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(commands, f, indent=2)

def generate_review_report(stats: Dict, classification_stats: Dict, low_confidence: List[Dict], output_file: str):
    """Generate a report for manual review"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Command Classification Report\n\n")
        
        f.write("## Overall Statistics\n")
        f.write(f"Total commands processed: {stats['total_commands']}\n\n")
        
        f.write("## Classification Results\n")
        for cmd_type, count in classification_stats.items():
            percentage = (count / stats['total_commands']) * 100
            f.write(f"- {cmd_type}: {count} ({percentage:.1f}%)\n")
        f.write("\n")
        
        f.write("## Default Value Patterns\n")
        f.write(f"- Null defaults: {stats['null_defaults']}\n")
        f.write(f"- Boolean defaults: {stats['boolean_defaults']}\n")
        f.write(f"- Integer defaults: {stats['integer_defaults']}\n")
        f.write(f"- Float defaults: {stats['float_defaults']}\n")
        f.write(f"- String defaults: {stats['string_defaults']}\n\n")
        
        f.write("## Commands Needing Manual Review (Confidence < 70%)\n")
        f.write(f"Total: {len(low_confidence)} commands\n\n")
        
        for cmd in low_confidence[:50]:  # Show first 50
            f.write(f"- `{cmd['command']}`: {cmd['type']} ({cmd['confidence']:.2f}) - default: '{cmd['defaultValue']}'\n")
        
        if len(low_confidence) > 50:
            f.write(f"\n... and {len(low_confidence) - 50} more commands\n")
        
        f.write("\n## Most Common Command Prefixes\n")
        sorted_prefixes = sorted(stats['common_prefixes'].items(), key=lambda x: x[1], reverse=True)
        for prefix, count in sorted_prefixes[:20]:
            f.write(f"- {prefix}: {count} commands\n")

def main():
    input_file = "data/parsed_commands.json"
    output_file = "data/commands_with_types.json"
    report_file = "data/classification_report.md"
    
    print("Loading commands...")
    commands = load_commands(input_file)
    
    print("Analyzing command patterns...")
    stats = analyze_command_patterns(commands)
    
    print("Classifying command types...")
    classified_commands, classification_stats, low_confidence = add_type_classification(commands)
    
    print("Saving classified commands...")
    save_classified_commands(classified_commands, output_file)
    
    print("Generating review report...")
    generate_review_report(stats, classification_stats, low_confidence, report_file)
    
    print(f"\nClassification complete!")
    print(f"- Input: {len(commands)} commands")
    print(f"- Output: {output_file}")
    print(f"- Report: {report_file}")
    print(f"- Commands needing manual review: {len(low_confidence)}")
    
    print("\nType distribution:")
    for cmd_type, count in classification_stats.items():
        percentage = (count / len(commands)) * 100
        print(f"  {cmd_type}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()