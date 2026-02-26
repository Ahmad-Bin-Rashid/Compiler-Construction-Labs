"""
Buffer Manager for Double Buffering in Lexical Analysis
Week 2: CC Lab - Double Buffering Using Multi-Threading

This module implements a BufferManager class with two alternating buffers
for efficient character reading in lexical analysis.
"""

import threading
from typing import Optional
from enum import Enum


class BufferState(Enum):
    """State of a buffer in the double buffering system."""
    EMPTY = 0       # Buffer is empty, ready to be filled
    FILLING = 1     # Buffer is currently being filled by reader thread
    FULL = 2        # Buffer is full, ready to be processed
    PROCESSING = 3  # Buffer is currently being processed by scanner


# Sentinel character to mark end of buffer content
SENTINEL = '\x00'
EOF_MARKER = '\x1a'  # ASCII EOF character (Ctrl+Z)


class BufferManager:
    """
    Manages two alternating buffers for double buffering.
    
    Attributes:
        buffer_size: Size of each buffer in bytes
        buffers: List of two character buffers
        buffer_states: State of each buffer
        active_buffer: Index of currently active buffer (0 or 1)
        positions: Current read position in each buffer
        content_lengths: Actual content length in each buffer
    """
    
    def __init__(self, buffer_size: int = 4096):
        """
        Initialize the BufferManager with two buffers.
        
        Args:
            buffer_size: Size of each buffer (default 4096 bytes)
        """
        self.buffer_size = buffer_size
        
        # Create two buffers with sentinel at the end
        # Extra space for sentinel character
        self.buffers = [
            [SENTINEL] * (buffer_size + 1),
            [SENTINEL] * (buffer_size + 1)
        ]
        
        # Buffer states
        self.buffer_states = [BufferState.EMPTY, BufferState.EMPTY]
        
        # Active buffer index (0 or 1)
        self.active_buffer = 0
        
        # Current position in each buffer
        self.positions = [0, 0]
        
        # Actual content length in each buffer (excluding sentinel)
        self.content_lengths = [0, 0]
        
        # Pointers for lexical analysis
        self.lexeme_begin = 0
        self.lexeme_begin_buffer = 0
        self.forward = 0
        self.forward_buffer = 0
        
        # Thread synchronization lock
        self.lock = threading.Lock()
        
        # Statistics
        self.buffer_switches = 0
        self.total_chars_processed = 0
        
        # EOF flag
        self.eof_reached = False
        
    def fill_buffer(self, buffer_idx: int, content: str) -> int:
        """
        Fill a buffer with content from file.
        
        Args:
            buffer_idx: Index of buffer to fill (0 or 1)
            content: String content to put in buffer
            
        Returns:
            Number of characters written to buffer
        """
        with self.lock:
            if buffer_idx not in (0, 1):
                raise ValueError("Buffer index must be 0 or 1")
            
            self.buffer_states[buffer_idx] = BufferState.FILLING
        
        # Copy content to buffer
        content_len = min(len(content), self.buffer_size)
        for i in range(content_len):
            self.buffers[buffer_idx][i] = content[i]
        
        # Add sentinel at the end of content
        self.buffers[buffer_idx][content_len] = SENTINEL
        
        with self.lock:
            self.content_lengths[buffer_idx] = content_len
            self.positions[buffer_idx] = 0
            self.buffer_states[buffer_idx] = BufferState.FULL
        
        return content_len
    
    def get_char_at(self, buffer_idx: int, position: int) -> str:
        """
        Get character at specific position in buffer.
        
        Args:
            buffer_idx: Buffer index (0 or 1)
            position: Position in buffer
            
        Returns:
            Character at position or SENTINEL if out of bounds
        """
        if position < 0 or position > self.buffer_size:
            return SENTINEL
        return self.buffers[buffer_idx][position]
    
    def get_active_buffer_index(self) -> int:
        """Get index of currently active buffer."""
        with self.lock:
            return self.active_buffer
    
    def get_inactive_buffer_index(self) -> int:
        """Get index of inactive buffer (for filling)."""
        with self.lock:
            return 1 - self.active_buffer
    
    def switch_buffer(self) -> bool:
        """
        Switch to the other buffer.
        
        Returns:
            True if switch successful, False if other buffer not ready
        """
        with self.lock:
            other_buffer = 1 - self.active_buffer
            
            if self.buffer_states[other_buffer] != BufferState.FULL:
                return False
            
            # Mark current buffer as empty (ready for refill)
            self.buffer_states[self.active_buffer] = BufferState.EMPTY
            
            # Switch to other buffer
            self.active_buffer = other_buffer
            self.buffer_states[other_buffer] = BufferState.PROCESSING
            self.positions[other_buffer] = 0
            
            self.buffer_switches += 1
            
            return True
    
    def is_buffer_ready(self, buffer_idx: int) -> bool:
        """Check if buffer is full and ready for processing."""
        with self.lock:
            return self.buffer_states[buffer_idx] == BufferState.FULL
    
    def is_buffer_empty(self, buffer_idx: int) -> bool:
        """Check if buffer is empty and ready for filling."""
        with self.lock:
            return self.buffer_states[buffer_idx] == BufferState.EMPTY
    
    def mark_buffer_empty(self, buffer_idx: int):
        """Mark buffer as empty (ready to be refilled)."""
        with self.lock:
            self.buffer_states[buffer_idx] = BufferState.EMPTY
    
    def mark_buffer_processing(self, buffer_idx: int):
        """Mark buffer as being processed."""
        with self.lock:
            self.buffer_states[buffer_idx] = BufferState.PROCESSING
    
    def get_buffer_state(self, buffer_idx: int) -> BufferState:
        """Get current state of a buffer."""
        with self.lock:
            return self.buffer_states[buffer_idx]
    
    def get_content_length(self, buffer_idx: int) -> int:
        """Get actual content length in buffer."""
        with self.lock:
            return self.content_lengths[buffer_idx]
    
    def set_eof(self):
        """Mark that EOF has been reached."""
        with self.lock:
            self.eof_reached = True
    
    def is_eof(self) -> bool:
        """Check if EOF has been reached."""
        with self.lock:
            return self.eof_reached
    
    def get_statistics(self) -> dict:
        """
        Get buffer usage statistics.
        
        Returns:
            Dictionary with buffer statistics
        """
        with self.lock:
            return {
                'buffer_size': self.buffer_size,
                'buffer_switches': self.buffer_switches,
                'total_chars_processed': self.total_chars_processed,
                'active_buffer': self.active_buffer,
                'buffer_states': [state.name for state in self.buffer_states],
                'content_lengths': self.content_lengths.copy()
            }
    
    def reset(self):
        """Reset buffer manager to initial state."""
        with self.lock:
            for i in range(2):
                self.buffers[i] = [SENTINEL] * (self.buffer_size + 1)
                self.buffer_states[i] = BufferState.EMPTY
                self.positions[i] = 0
                self.content_lengths[i] = 0
            
            self.active_buffer = 0
            self.lexeme_begin = 0
            self.lexeme_begin_buffer = 0
            self.forward = 0
            self.forward_buffer = 0
            self.buffer_switches = 0
            self.total_chars_processed = 0
            self.eof_reached = False


if __name__ == "__main__":
    # Simple test of BufferManager
    print("Testing BufferManager...")
    
    bm = BufferManager(buffer_size=10)
    
    # Fill first buffer
    bm.fill_buffer(0, "Hello World")
    print(f"Buffer 0 content length: {bm.get_content_length(0)}")
    print(f"Buffer 0 state: {bm.get_buffer_state(0).name}")
    
    # Read characters
    for i in range(12):
        char = bm.get_char_at(0, i)
        print(f"Position {i}: '{char}' (ord={ord(char)})")
    
    print("\nStatistics:", bm.get_statistics())
