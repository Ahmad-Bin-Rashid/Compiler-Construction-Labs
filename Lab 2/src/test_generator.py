"""
Test File Generator for Double Buffering Lab
Week 2: CC Lab - Double Buffering Using Multi-Threading

This module generates large source code files for testing
the performance of single vs double buffering.
"""

import argparse
import os
import random
from typing import Optional


# Sample code templates that look like real source code
CODE_TEMPLATES = [
    # Function template
    '''
int {func_name}(int {param1}, int {param2}) {{
    int {var1} = {param1} + {param2};
    int {var2} = {param1} * {param2};
    
    if ({var1} > {threshold}) {{
        {var2} = {var1} - {threshold};
    }} else {{
        {var2} = {threshold} - {var1};
    }}
    
    return {var2};
}}
''',
    
    # Loop template
    '''
void {func_name}() {{
    int counter = 0;
    float result = 0.0;
    
    while (counter < {loop_count}) {{
        result = result + {increment};
        counter = counter + 1;
    }}
    
    printf("Result: %f\\n", result);
}}
''',
    
    # Array processing template
    '''
void process_{func_name}(int arr[], int size) {{
    int sum = 0;
    int max = arr[0];
    int min = arr[0];
    
    for (int i = 0; i < size; i++) {{
        sum += arr[i];
        if (arr[i] > max) max = arr[i];
        if (arr[i] < min) min = arr[i];
    }}
    
    int average = sum / size;
    printf("Sum: %d, Avg: %d, Max: %d, Min: %d\\n", sum, average, max, min);
}}
''',
    
    # Struct definition template
    '''
typedef struct {{
    int {field1};
    float {field2};
    char {field3}[{array_size}];
    int {field4};
}} {struct_name};

{struct_name} create_{struct_name}(int val1, float val2) {{
    {struct_name} obj;
    obj.{field1} = val1;
    obj.{field2} = val2;
    obj.{field4} = val1 + (int)val2;
    return obj;
}}
''',
    
    # Conditional template
    '''
int check_{func_name}(int value) {{
    int result = 0;
    
    if (value < {val1}) {{
        result = {val1} - value;
    }} else if (value < {val2}) {{
        result = {val2} - value;
    }} else if (value < {val3}) {{
        result = {val3} - value;
    }} else {{
        result = value - {val3};
    }}
    
    return result;
}}
''',
    
    # String processing template
    '''
int process_string_{func_name}(char* str) {{
    int length = 0;
    int spaces = 0;
    int digits = 0;
    
    while (str[length] != '\\0') {{
        if (str[length] == ' ') spaces++;
        if (str[length] >= '0' && str[length] <= '9') digits++;
        length++;
    }}
    
    return length + spaces * 2 + digits * 3;
}}
''',
]

# Word lists for generating varied identifiers
NOUNS = ['data', 'result', 'value', 'count', 'index', 'buffer', 'size', 'length', 
         'array', 'list', 'item', 'element', 'node', 'tree', 'graph', 'table',
         'record', 'field', 'key', 'hash', 'stack', 'queue', 'heap', 'cache']

VERBS = ['process', 'compute', 'calculate', 'transform', 'convert', 'analyze',
         'validate', 'parse', 'format', 'encode', 'decode', 'compress', 'sort',
         'search', 'filter', 'merge', 'split', 'update', 'insert', 'delete']

ADJECTIVES = ['max', 'min', 'total', 'current', 'previous', 'next', 'first',
              'last', 'temp', 'new', 'old', 'valid', 'active', 'primary', 'main']


def generate_identifier() -> str:
    """Generate a random identifier name."""
    patterns = [
        lambda: f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}",
        lambda: f"{random.choice(VERBS)}_{random.choice(NOUNS)}",
        lambda: f"{random.choice(NOUNS)}_{random.randint(1, 99)}",
        lambda: f"{random.choice(ADJECTIVES)}{random.choice(NOUNS).title()}",
    ]
    return random.choice(patterns)()


def generate_code_block() -> str:
    """Generate a random code block from templates."""
    template = random.choice(CODE_TEMPLATES)
    
    # Fill in template variables
    return template.format(
        func_name=generate_identifier(),
        param1=generate_identifier(),
        param2=generate_identifier(),
        var1=generate_identifier(),
        var2=generate_identifier(),
        threshold=random.randint(10, 1000),
        loop_count=random.randint(100, 100000),
        increment=random.uniform(0.001, 1.0),
        field1=generate_identifier(),
        field2=generate_identifier(),
        field3=generate_identifier(),
        field4=generate_identifier(),
        array_size=random.randint(16, 256),
        struct_name=generate_identifier().title().replace('_', ''),
        val1=random.randint(10, 50),
        val2=random.randint(51, 100),
        val3=random.randint(101, 200),
    )


def generate_main_function() -> str:
    """Generate a main function."""
    return '''
int main() {{
    int counter = 0;
    float result = 3.14159;
    
    while (counter < 1000000) {{
        result = result + 0.001;
        counter = counter + 1;
    }}
    
    return 0;
}}
'''


def generate_header() -> str:
    """Generate file header with includes and comments."""
    return '''/*
 * Auto-generated source file for testing double buffering
 * Week 2: CC Lab - Double Buffering Using Multi-Threading
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Global constants
#define MAX_SIZE 1024
#define BUFFER_SIZE 4096
#define DEFAULT_VALUE 0

'''


def generate_comment_block() -> str:
    """Generate a random comment block."""
    comments = [
        "// Process the input data\n",
        "/* Multi-line comment\n * explaining the algorithm\n * and its complexity\n */\n",
        "// TODO: Optimize this function\n",
        "// FIXME: Handle edge cases\n",
        "/* Important: This function has O(n) complexity */\n",
        "// Author: Student Name\n// Date: 2024-01-01\n",
    ]
    return random.choice(comments)


def parse_size(size_str: str) -> int:
    """
    Parse size string like '100KB' or '1MB' to bytes.
    
    Args:
        size_str: Size string (e.g., '100KB', '1MB', '500000')
        
    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()
    
    if size_str.endswith('KB'):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith('MB'):
        return int(float(size_str[:-2]) * 1024 * 1024)
    elif size_str.endswith('GB'):
        return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
    else:
        return int(size_str)


def generate_test_file(output_path: str, target_size: int, verbose: bool = False) -> int:
    """
    Generate a test source code file of approximately target size.
    
    Args:
        output_path: Path for output file
        target_size: Target file size in bytes
        verbose: Print progress
        
    Returns:
        Actual file size in bytes
    """
    content_parts = []
    current_size = 0
    
    # Add header
    header = generate_header()
    content_parts.append(header)
    current_size += len(header)
    
    if verbose:
        print(f"Generating file of approximately {target_size:,} bytes...")
    
    # Generate code blocks until we reach target size
    block_count = 0
    while current_size < target_size:
        # Occasionally add comments
        if random.random() < 0.2:
            comment = generate_comment_block()
            content_parts.append(comment)
            current_size += len(comment)
        
        # Add code block
        block = generate_code_block()
        content_parts.append(block)
        current_size += len(block)
        block_count += 1
        
        if verbose and block_count % 100 == 0:
            progress = min(100, current_size * 100 // target_size)
            print(f"  Progress: {progress}% ({current_size:,} bytes)")
    
    # Add main function at the end
    main = generate_main_function()
    content_parts.append(main)
    
    # Write to file
    content = ''.join(content_parts)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    actual_size = os.path.getsize(output_path)
    
    if verbose:
        print(f"Generated: {output_path}")
        print(f"  Size: {actual_size:,} bytes")
        print(f"  Code blocks: {block_count}")
    
    return actual_size


def generate_simple_test_file(output_path: str) -> int:
    """
    Generate the simple test file from the lab specification.
    
    Args:
        output_path: Path for output file
        
    Returns:
        File size in bytes
    """
    content = '''int main() {
    int counter = 0;
    float result = 3.14159;
    
    while (counter < 1000000) {
        result = result + 0.001;
        counter = counter + 1;
    }
    
    return 0;
}
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return os.path.getsize(output_path)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Generate test files for double buffering lab'
    )
    parser.add_argument(
        '--size', '-s',
        type=str,
        default='100KB',
        help='Target file size (e.g., 100KB, 500KB, 1MB)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='test_program.txt',
        help='Output file path'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Generate simple test file from lab specification'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print progress information'
    )
    parser.add_argument(
        '--multiple',
        type=str,
        help='Generate multiple sizes (comma-separated, e.g., "100KB,500KB,1MB")'
    )
    
    args = parser.parse_args()
    
    if args.simple:
        size = generate_simple_test_file(args.output)
        print(f"Generated simple test file: {args.output} ({size} bytes)")
        return
    
    if args.multiple:
        sizes = [s.strip() for s in args.multiple.split(',')]
        for size_str in sizes:
            target_size = parse_size(size_str)
            base_name = os.path.splitext(args.output)[0]
            ext = os.path.splitext(args.output)[1] or '.txt'
            output_path = f"{base_name}_{size_str.lower()}{ext}"
            generate_test_file(output_path, target_size, args.verbose)
    else:
        target_size = parse_size(args.size)
        generate_test_file(args.output, target_size, args.verbose)


if __name__ == "__main__":
    main()
