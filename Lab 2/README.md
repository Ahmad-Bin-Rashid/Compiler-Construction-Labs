# Week 2: Double Buffering Using Multi-Threading

## CC Lab - Compiler Construction

This lab implements a double buffering system with multi-threading for efficient lexical analysis I/O operations.

## Learning Objectives
- Understand the concept of double buffering in lexical analysis
- Implement multi-threaded I/O for efficient file reading
- Manage buffer transitions seamlessly
- Handle end-of-file conditions properly

## Theoretical Background

### Double Buffering Concept

In lexical analysis, reading input character-by-character is inefficient. Double buffering uses two alternating buffers to minimize I/O operations. While one buffer is being processed, the other can be refilled asynchronously.

```
+-------------------+-------------------+
|     Buffer 1      |     Buffer 2      |
| [a][b][c][...][E] | [x][y][z][...][E] |
+-------------------+-------------------+
        ↑
    lexemeBegin
             ↑
          forward
```

- **lexemeBegin**: Points to the start of the current lexeme
- **forward**: Scans ahead to find the end of the lexeme
- **E**: Sentinel character (EOF marker)

### Multi-Threading Benefit

Using separate threads for:
1. **Reader Thread**: Reads from file into inactive buffer
2. **Scanner Thread**: Processes active buffer for tokens

This overlap of I/O and processing improves performance significantly.

## Project Structure

```
lab2/
│
├── screenshots/           # Screenshots of Output
│
├── src/
│ ├── buffer_manager.py    # Core double buffer implementation
│ ├── threaded_reader.py   # Producer-consumer with semaphores & condition variables
│ ├── char_stream.py       # Clean interface for lexical analyzer
│ ├── single_buffer.py     # Single buffer baseline for comparison
│ ├── test_generator.py    # Utility to generate large test files
│ └── main.py              # Main driver with performance benchmarks
│
├── docs/
│ ├── lab2 report.pdf      # Detailed Report including implementation details and performance review
| └── lab2 manual.pdf
|
└── README.md              # This documentation

```

## File Descriptions

### buffer_manager.py
Core `BufferManager` class with:
- Two buffers of configurable size (default 4096 bytes)
- Sentinel markers at buffer ends
- Thread-safe buffer state tracking
- Statistics collection

### threaded_reader.py
Producer-consumer pattern implementations:
- `ThreadedReaderSemaphore`: Uses semaphores for synchronization
- `ThreadedReaderCondVar`: Uses condition variables for synchronization
- Factory function `create_threaded_reader()` to select implementation

### char_stream.py
Clean character stream interface:
- `get_next_char()` - Returns next character
- `unget_char()` - Puts back one character
- `get_lexeme()` - Returns current lexeme
- `reset_lexeme_begin()` - Marks new lexeme start

### single_buffer.py
Single buffer baseline for performance comparison:
- Sequential read-process-read pattern
- Same interface as double buffer
- Collects timing statistics for comparison

### test_generator.py
Test file generator:
- Creates realistic source code files
- Configurable size (100KB, 500KB, 1MB, etc.)
- Uses varied code templates for realistic content

### main.py
Main benchmark driver:
- Runs performance comparison
- Displays buffer transition demos
- Generates formatted reports

## Usage

### Quick Start

```bash
# Navigate to src folder
cd src

# Run with default settings (generates 100KB test file if needed)
python main.py

# Generate specific size test file and run
python main.py --genera te 500KB

# Use specific buffer size
python main.py --buffer-size 8192

# Use condition variables instead of semaphores
python main.py --sync-method cv
```

### Command Line Options

```
usage: main.py [-h] [--input INPUT] [--buffer-size BUFFER_SIZE]
               [--sync-method {sem,semaphore,cv,condition}] [--runs RUNS]
               [--generate GENERATE] [--no-demo] [--verbose]

Options:
  --input, -i       Input file path (default: test_program.txt)
  --buffer-size, -b Buffer size in bytes (default: 4096)
  --sync-method, -s Synchronization method: sem/semaphore or cv/condition
  --runs, -r        Number of benchmark runs (default: 3)
  --generate, -g    Generate test file of specified size (e.g., 100KB, 500KB)
  --no-demo         Skip buffer transition demo
  --verbose, -v     Verbose output
```

### Test File Generator

```bash
# Generate 100KB test file
python test_generator.py --size 100KB --output test_program.txt

# Generate multiple sizes
python test_generator.py --multiple "100KB,500KB,1MB" --output test.txt

# Generate simple test file from lab spec
python test_generator.py --simple --output simple_test.txt
```

## Sample Output

```
============================================================
  Double Buffering Using Multi-Threading
============================================================
Week 2: CC Lab

Test File: test_program.txt
File Size: 102.45 KB
Buffer Size: 4096 bytes
Sync Method: semaphore

Running benchmark (3 runs each)...
  Single buffer: [1] [2] [3]
  Double buffer: [1] [2] [3]

============================================================
  Buffer Configuration
============================================================
- Buffer Size: 4096 bytes
- Total File Size: 104905 bytes (102.45 KB)
- Synchronization Method: semaphore

============================================================
  Reading Statistics
============================================================

Single Buffer Mode:
  - Buffer refills: 26
  - Average refill time: 0.45ms
  - Total I/O wait time: 11.70ms

Double Buffer Mode:
  - Total buffer switches: 25
  - Read operations: 26
  - Average fill time: 0.42ms

============================================================
  Performance Comparison
============================================================

Processing time (average of 3 runs):
  - Single buffer: 85.23ms
  - Double buffer: 78.45ms

  Performance improvement: 7.9%
  (Double buffering is faster)

Characters processed: 104905

============================================================
  Buffer Transition Demo
============================================================

[Transition 1]
  Position: 102
  From Buffer 0 -> Buffer 1
  [Buffer 0 end] ...int main()
  [Buffer 1 start]  {\n    int...

============================================================
  Summary
============================================================
Characters processed: 104905
EOF reached successfully.
```

## Implementation Details

### Synchronization Methods

#### Semaphores
- `empty_sem`: Counts empty buffers available (initially 2)
- `full_sem`: Counts filled buffers available (initially 0)
- Classic producer-consumer synchronization

#### Condition Variables
- `buffer_available`: Signals when a buffer is filled
- `buffer_empty`: Signals when a buffer is processed
- More flexible, mutex-based approach

### Buffer States

```python
class BufferState(Enum):
    EMPTY = 0       # Ready to be filled
    FILLING = 1     # Currently being filled
    FULL = 2        # Ready to be processed
    PROCESSING = 3  # Currently being processed
```

### Sentinel Character

The sentinel character (`\x00`) marks the end of valid content in each buffer, allowing efficient boundary detection without constant bounds checking.

## Important Notes

### Python GIL Limitation

Python's Global Interpreter Lock (GIL) limits true CPU parallelism. However:
- I/O operations release the GIL
- File reading can still benefit from threading
- The concept demonstration remains valid
- For maximum performance, implement in C/C++

### Edge Cases Handled

1. **EOF Detection**: Proper thread termination when file ends
2. **Lexemes Spanning Buffers**: Characters saved when lexeme crosses boundary
3. **Small Files**: Works with files smaller than buffer size
4. **Empty Files**: Graceful handling of empty input


## Testing Commands

```bash
# Test with different file sizes
python main.py --generate 100KB --runs 5
python main.py --generate 500KB --runs 5
python main.py --generate 1MB --runs 5

# Compare synchronization methods
python main.py --sync-method semaphore --runs 5
python main.py --sync-method cv --runs 5

# Test with different buffer sizes
python main.py --buffer-size 1024 --runs 3
python main.py --buffer-size 4096 --runs 3
python main.py --buffer-size 8192 --runs 3
```

## Author

Ahmad Bin Rashid - 2023-CS-53
