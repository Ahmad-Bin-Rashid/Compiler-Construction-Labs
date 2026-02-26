"""
Single Buffer Implementation for Comparison
Week 2: CC Lab - Double Buffering Using Multi-Threading

This module provides a single-buffer baseline implementation
for performance comparison with double buffering.
"""

import time
from typing import Optional


class SingleBufferReader:
    """
    Single buffer reader - sequential read-process-read pattern.
    
    This serves as a baseline for comparing with double buffering.
    No threading - reads block while waiting for I/O.
    """
    
    def __init__(self, buffer_size: int = 4096):
        """
        Initialize single buffer reader.
        
        Args:
            buffer_size: Size of the buffer in bytes
        """
        self.buffer_size = buffer_size
        self.buffer = []
        self.position = 0
        self.lexeme_begin = 0
        
        self.file_handle = None
        self.file_path: Optional[str] = None
        
        # EOF tracking
        self._eof = False
        self._file_exhausted = False
        
        # Statistics
        self.total_chars_read = 0
        self.buffer_refills = 0
        self.refill_times = []
        self.total_refill_time = 0.0
        self.processing_waits = 0  # Times processing had to wait for I/O
        
    def open(self, file_path: str):
        """
        Open a file for reading.
        
        Args:
            file_path: Path to file
        """
        self.file_path = file_path
        self.file_handle = open(file_path, 'r', encoding='utf-8', errors='replace')
        
        # Reset state
        self.buffer = []
        self.position = 0
        self.lexeme_begin = 0
        self._eof = False
        self._file_exhausted = False
        
        # Reset statistics
        self.total_chars_read = 0
        self.buffer_refills = 0
        self.refill_times = []
        self.total_refill_time = 0.0
        self.processing_waits = 0
        
        # Initial buffer fill
        self._refill_buffer()
    
    def _refill_buffer(self):
        """
        Refill buffer from file.
        
        This blocks until I/O completes - the key difference from double buffering.
        """
        if self._file_exhausted or self.file_handle is None:
            return False
        
        # Record that processing had to wait for I/O
        self.processing_waits += 1
        
        # Time the I/O operation
        start_time = time.perf_counter()
        content = self.file_handle.read(self.buffer_size)
        refill_time = time.perf_counter() - start_time
        
        if not content:
            self._file_exhausted = True
            return False
        
        # Handle lexeme spanning buffer boundary
        # Keep the lexeme part that might still be needed
        if self.lexeme_begin < len(self.buffer):
            # Save lexeme portion from old buffer
            lexeme_portion = self.buffer[self.lexeme_begin:]
            self.buffer = lexeme_portion + list(content)
            self.position = len(lexeme_portion)
            self.lexeme_begin = 0
        else:
            self.buffer = list(content)
            self.position = 0
            self.lexeme_begin = 0
        
        # Update statistics
        self.buffer_refills += 1
        self.refill_times.append(refill_time)
        self.total_refill_time += refill_time
        
        return True
    
    def get_next_char(self) -> str:
        """
        Get the next character from input.
        
        Returns:
            Next character, or empty string if EOF
        """
        # Check if we need to refill buffer
        if self.position >= len(self.buffer):
            if self._file_exhausted:
                self._eof = True
                return ''
            
            # Block and wait for I/O (the inefficiency we're measuring)
            if not self._refill_buffer():
                self._eof = True
                return ''
        
        # Get character
        if self.position >= len(self.buffer):
            self._eof = True
            return ''
        
        char = self.buffer[self.position]
        self.position += 1
        self.total_chars_read += 1
        
        return char
    
    def unget_char(self):
        """Put back one character."""
        if self.position > self.lexeme_begin:
            self.position -= 1
            self.total_chars_read -= 1
    
    def get_lexeme(self) -> str:
        """Get current lexeme (from lexeme_begin to position)."""
        if self.lexeme_begin < len(self.buffer) and self.position <= len(self.buffer):
            return ''.join(self.buffer[self.lexeme_begin:self.position])
        return ''
    
    def reset_lexeme_begin(self):
        """Mark start of new lexeme at current position."""
        # If we've moved past the old lexeme, we can trim the buffer
        # to save memory (optional optimization)
        self.lexeme_begin = self.position
    
    def peek_char(self) -> str:
        """Peek at next character without advancing."""
        char = self.get_next_char()
        if char:
            self.unget_char()
        return char
    
    def is_eof(self) -> bool:
        """Check if EOF reached."""
        return self._eof
    
    def close(self):
        """Close the file."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def get_statistics(self) -> dict:
        """
        Get reading statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        avg_refill_time = (sum(self.refill_times) / len(self.refill_times) 
                          if self.refill_times else 0)
        
        return {
            'buffer_size': self.buffer_size,
            'total_chars_read': self.total_chars_read,
            'buffer_refills': self.buffer_refills,
            'processing_waits': self.processing_waits,
            'total_refill_time_ms': self.total_refill_time * 1000,
            'average_refill_time_ms': avg_refill_time * 1000,
            'refill_times': self.refill_times
        }
    
    def get_file_size(self) -> int:
        """Get size of opened file."""
        if self.file_path:
            import os
            return os.path.getsize(self.file_path)
        return 0


def process_file_single_buffer(file_path: str, buffer_size: int = 4096) -> dict:
    """
    Process entire file using single buffer and return statistics.
    
    This simulates lexical analysis by reading all characters.
    
    Args:
        file_path: Path to file to process
        buffer_size: Buffer size to use
        
    Returns:
        Dictionary with processing statistics
    """
    reader = SingleBufferReader(buffer_size)
    
    start_time = time.perf_counter()
    
    reader.open(file_path)
    
    # Process all characters (simulating lexical analysis)
    char_count = 0
    while True:
        char = reader.get_next_char()
        if not char:
            break
        char_count += 1
        
        # Simulate some minimal processing
        # (In real lexer, would be token recognition)
        _ = ord(char)
    
    processing_time = time.perf_counter() - start_time
    
    stats = reader.get_statistics()
    stats['total_processing_time_ms'] = processing_time * 1000
    stats['file_size'] = reader.get_file_size()
    
    reader.close()
    
    return stats


if __name__ == "__main__":
    import os
    
    print("Testing SingleBufferReader...")
    
    # Create a test file
    test_content = "Hello World! " * 1000
    test_file = "test_single.tmp"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Test basic functionality
        reader = SingleBufferReader(buffer_size=100)
        reader.open(test_file)
        
        # Read some characters
        chars = []
        for _ in range(50):
            char = reader.get_next_char()
            if not char:
                break
            chars.append(char)
        
        print(f"Read: {''.join(chars)}")
        
        # Test lexeme extraction
        reader.reset_lexeme_begin()
        for _ in range(5):
            reader.get_next_char()
        print(f"Lexeme: '{reader.get_lexeme()}'")
        
        # Test unget
        reader.unget_char()
        print(f"After unget: '{reader.get_next_char()}'")
        
        reader.close()
        
        # Test full file processing
        print("\nProcessing full file...")
        stats = process_file_single_buffer(test_file, buffer_size=100)
        print(f"Statistics: {stats}")
        
    finally:
        os.remove(test_file)
    
    print("\nTest completed!")
