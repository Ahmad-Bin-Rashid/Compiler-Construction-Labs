"""
Main Driver for Double Buffering Performance Comparison
Week 2: CC Lab - Double Buffering Using Multi-Threading

This module runs performance benchmarks comparing single-buffer
vs double-buffer approaches with multi-threading.
"""

import argparse
import os
import sys
import time
from typing import Optional, Tuple, List

from buffer_manager import BufferManager
from char_stream import CharacterStream, SimpleCharacterStream
from single_buffer import SingleBufferReader, process_file_single_buffer
from threaded_reader import SyncMethod
from test_generator import generate_test_file, parse_size


def print_header(title: str, char: str = '='):
    """Print a section header."""
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}")


def format_time(ms: float) -> str:
    """Format time in appropriate units."""
    if ms < 1:
        return f"{ms * 1000:.2f}us"
    elif ms < 1000:
        return f"{ms:.2f}ms"
    else:
        return f"{ms / 1000:.2f}s"


def format_size(bytes_count: int) -> str:
    """Format size in appropriate units."""
    if bytes_count < 1024:
        return f"{bytes_count} bytes"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.2f} KB"
    else:
        return f"{bytes_count / (1024 * 1024):.2f} MB"


def process_file_double_buffer(file_path: str, buffer_size: int = 4096,
                                sync_method: SyncMethod = SyncMethod.SEMAPHORE,
                                collect_transitions: bool = False) -> dict:
    """
    Process entire file using double buffering and return statistics.
    
    Args:
        file_path: Path to file to process
        buffer_size: Buffer size to use
        sync_method: Synchronization method
        collect_transitions: Whether to collect transition demo data
        
    Returns:
        Dictionary with processing statistics
    """
    bm = BufferManager(buffer_size)
    stream = CharacterStream(bm, sync_method)
    
    start_time = time.perf_counter()
    
    stream.open(file_path)
    
    # Process all characters (simulating lexical analysis)
    char_count = 0
    transition_chars = []  # Store chars around transitions for demo
    last_transition_count = 0
    
    while True:
        char = stream.get_next_char()
        if not char:
            break
        char_count += 1
        
        # Collect transition demo data
        if collect_transitions:
            current_transitions = len(stream.buffer_transitions)
            if current_transitions > last_transition_count:
                # New transition occurred
                last_transition_count = current_transitions
        
        # Simulate minimal processing
        _ = ord(char)
    
    processing_time = time.perf_counter() - start_time
    
    stats = stream.get_statistics()
    stats['total_processing_time_ms'] = processing_time * 1000
    stats['file_size'] = os.path.getsize(file_path)
    stats['char_count'] = char_count
    stats['sync_method'] = sync_method.value
    
    stream.close()
    
    return stats


def demonstrate_buffer_transitions(file_path: str, buffer_size: int = 100,
                                   num_transitions: int = 3) -> List[dict]:
    """
    Demonstrate buffer transitions by showing characters around switch points.
    
    Args:
        file_path: Path to file
        buffer_size: Small buffer size to force transitions
        num_transitions: Number of transitions to capture
        
    Returns:
        List of transition demonstrations
    """
    bm = BufferManager(buffer_size)
    stream = CharacterStream(bm, SyncMethod.SEMAPHORE)
    
    stream.open(file_path)
    
    transitions_captured = []
    chars_buffer = []  # Rolling buffer of recent chars
    position = 0
    last_transition_count = 0
    
    while len(transitions_captured) < num_transitions:
        char = stream.get_next_char()
        if not char:
            break
        
        position += 1
        chars_buffer.append(char)
        if len(chars_buffer) > 20:
            chars_buffer.pop(0)
        
        # Check for new transition
        current_transitions = len(stream.buffer_transitions)
        if current_transitions > last_transition_count:
            # Capture characters around this transition
            transition_info = stream.buffer_transitions[-1].copy()
            transition_info['chars_before'] = ''.join(chars_buffer[:-1])
            
            # Read a few more chars to show what's in new buffer
            chars_after = []
            for _ in range(5):
                c = stream.get_next_char()
                if not c:
                    break
                chars_after.append(c)
                position += 1
            
            transition_info['chars_after'] = ''.join(chars_after)
            transition_info['total_position'] = position
            transitions_captured.append(transition_info)
            
            # Add after chars to rolling buffer
            chars_buffer.extend(chars_after)
            last_transition_count = current_transitions
    
    stream.close()
    
    return transitions_captured


def run_benchmark(file_path: str, buffer_size: int = 4096,
                  sync_method: SyncMethod = SyncMethod.SEMAPHORE,
                  runs: int = 3) -> Tuple[dict, dict]:
    """
    Run benchmark comparing single vs double buffer.
    
    Args:
        file_path: Path to test file
        buffer_size: Buffer size to use
        sync_method: Synchronization method for double buffer
        runs: Number of runs for averaging
        
    Returns:
        Tuple of (single_buffer_stats, double_buffer_stats)
    """
    print(f"\nRunning benchmark ({runs} runs each)...")
    
    # Single buffer runs
    single_times = []
    single_stats = None
    print("  Single buffer:", end=" ", flush=True)
    for i in range(runs):
        stats = process_file_single_buffer(file_path, buffer_size)
        single_times.append(stats['total_processing_time_ms'])
        single_stats = stats
        print(f"[{i+1}]", end=" ", flush=True)
    print()
    
    # Double buffer runs
    double_times = []
    double_stats = None
    print("  Double buffer:", end=" ", flush=True)
    for i in range(runs):
        stats = process_file_double_buffer(file_path, buffer_size, sync_method)
        double_times.append(stats['total_processing_time_ms'])
        double_stats = stats
        print(f"[{i+1}]", end=" ", flush=True)
    print()
    
    # Calculate averages
    single_stats['average_time_ms'] = sum(single_times) / len(single_times)
    single_stats['all_times_ms'] = single_times
    double_stats['average_time_ms'] = sum(double_times) / len(double_times)
    double_stats['all_times_ms'] = double_times
    
    return single_stats, double_stats


def print_comparison_report(single_stats: dict, double_stats: dict,
                            buffer_size: int, file_path: str):
    """Print formatted comparison report."""
    
    print_header("Buffer Configuration")
    print(f"- Buffer Size: {buffer_size} bytes")
    print(f"- Total File Size: {single_stats['file_size']} bytes ({format_size(single_stats['file_size'])})")
    print(f"- Synchronization Method: {double_stats.get('sync_method', 'semaphore')}")
    
    print_header("Reading Statistics")
    
    # Single buffer stats
    print("\nSingle Buffer Mode:")
    print(f"  - Buffer refills: {single_stats['buffer_refills']}")
    print(f"  - Average refill time: {format_time(single_stats['average_refill_time_ms'])}")
    print(f"  - Total I/O wait time: {format_time(single_stats['total_refill_time_ms'])}")
    
    # Double buffer stats
    reader_stats = double_stats.get('reader', {})
    buffer_stats = double_stats.get('buffer_manager', {})
    
    print("\nDouble Buffer Mode:")
    print(f"  - Total buffer switches: {buffer_stats.get('buffer_switches', 'N/A')}")
    print(f"  - Read operations: {reader_stats.get('read_operations', 'N/A')}")
    print(f"  - Average fill time: {format_time(reader_stats.get('average_fill_time_ms', 0))}")
    
    print_header("Performance Comparison")
    
    single_time = single_stats['average_time_ms']
    double_time = double_stats['average_time_ms']
    
    print(f"\nProcessing time (average of {len(single_stats['all_times_ms'])} runs):")
    print(f"  - Single buffer: {format_time(single_time)}")
    print(f"  - Double buffer: {format_time(double_time)}")
    
    # Calculate improvement
    if double_time < single_time:
        improvement = ((single_time - double_time) / single_time) * 100
        print(f"\n  Performance improvement: {improvement:.1f}%")
        print(f"  (Double buffering is faster)")
    else:
        overhead = ((double_time - single_time) / single_time) * 100
        print(f"\n  Performance overhead: {overhead:.1f}%")
        print(f"  (Threading overhead exceeded I/O benefit)")
        print(f"  Note: Python's GIL limits true parallelism. In C/C++, ")
        print(f"        double buffering would show greater improvement.")
    
    print(f"\nCharacters processed: {single_stats['total_chars_read']}")


def print_transition_demo(transitions: List[dict]):
    """Print buffer transition demonstration."""
    
    print_header("Buffer Transition Demo")
    
    if not transitions:
        print("No transitions captured (file may be smaller than buffer)")
        return
    
    for i, trans in enumerate(transitions):
        print(f"\n[Transition {i + 1}]")
        print(f"  Position: {trans['total_position']}")
        print(f"  From Buffer {trans['from_buffer']} -> Buffer {trans['to_buffer']}")
        
        # Show characters before transition (escaping special chars)
        chars_before = trans['chars_before'][-10:] if len(trans['chars_before']) > 10 else trans['chars_before']
        chars_before_display = repr(chars_before)[1:-1]  # Remove quotes
        
        chars_after = trans['chars_after'][:10]
        chars_after_display = repr(chars_after)[1:-1]
        
        print(f"  [Buffer {trans['from_buffer']} end] ...{chars_before_display}")
        print(f"  [Buffer {trans['to_buffer']} start] {chars_after_display}...")


def ensure_test_file(file_path: str, size: str = "100KB", verbose: bool = False) -> str:
    """Ensure test file exists, generate if needed."""
    if not os.path.exists(file_path):
        print(f"Test file not found. Generating {size} test file...")
        target_size = parse_size(size)
        generate_test_file(file_path, target_size, verbose)
        print(f"Generated: {file_path}")
    return file_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Double Buffering Performance Comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py                          # Run with defaults
  python main.py --input myfile.c         # Use specific file
  python main.py --buffer-size 8192       # Use 8KB buffers
  python main.py --sync-method cv         # Use condition variables
  python main.py --generate 500KB         # Generate 500KB test file first
'''
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='test_program.txt',
        help='Input file path (default: test_program.txt)'
    )
    parser.add_argument(
        '--buffer-size', '-b',
        type=int,
        default=4096,
        help='Buffer size in bytes (default: 4096)'
    )
    parser.add_argument(
        '--sync-method', '-s',
        type=str,
        choices=['sem', 'semaphore', 'cv', 'condition'],
        default='semaphore',
        help='Synchronization method (default: semaphore)'
    )
    parser.add_argument(
        '--runs', '-r',
        type=int,
        default=3,
        help='Number of benchmark runs (default: 3)'
    )
    parser.add_argument(
        '--generate', '-g',
        type=str,
        help='Generate test file of specified size (e.g., 100KB, 500KB, 1MB)'
    )
    parser.add_argument(
        '--no-demo',
        action='store_true',
        help='Skip buffer transition demo'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Determine sync method
    if args.sync_method in ('cv', 'condition'):
        sync_method = SyncMethod.CONDITION_VARIABLE
    else:
        sync_method = SyncMethod.SEMAPHORE
    
    # Generate test file if requested
    if args.generate:
        target_size = parse_size(args.generate)
        print(f"Generating {args.generate} test file: {args.input}")
        generate_test_file(args.input, target_size, verbose=True)
    
    # Ensure test file exists
    if not os.path.exists(args.input):
        print(f"Test file '{args.input}' not found.")
        print("Generating default 100KB test file...")
        generate_test_file(args.input, 100 * 1024, verbose=args.verbose)
    
    file_size = os.path.getsize(args.input)
    
    print_header("Double Buffering Using Multi-Threading", '=')
    print(f"Week 2: CC Lab")
    print(f"\nTest File: {args.input}")
    print(f"File Size: {format_size(file_size)}")
    print(f"Buffer Size: {args.buffer_size} bytes")
    print(f"Sync Method: {sync_method.value}")
    
    # Run benchmark
    single_stats, double_stats = run_benchmark(
        args.input, 
        args.buffer_size,
        sync_method,
        args.runs
    )
    
    # Print comparison report
    print_comparison_report(single_stats, double_stats, args.buffer_size, args.input)
    
    # Show transition demo
    if not args.no_demo:
        # Use smaller buffer for demo to ensure transitions
        demo_buffer_size = min(1000, args.buffer_size)
        transitions = demonstrate_buffer_transitions(args.input, demo_buffer_size, 5)
        print_transition_demo(transitions)
    
    print_header("Summary")
    print(f"Characters processed: {single_stats['total_chars_read']}")
    print("EOF reached successfully.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
