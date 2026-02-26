"""
Character Stream Interface for Lexical Analysis
Week 2: CC Lab - Double Buffering Using Multi-Threading

This module provides a clean interface for the lexical analyzer
to read characters from the double-buffered input.
"""

import threading
import time
from typing import Optional, List, Tuple
from buffer_manager import BufferManager, BufferState, SENTINEL
from threaded_reader import (ThreadedReaderSemaphore, ThreadedReaderCondVar, 
                              SyncMethod, create_threaded_reader)


class CharacterStream:
    """
    Clean interface for lexical analyzer to read characters.
    
    Provides:
    - get_next_char(): Returns next character
    - unget_char(): Puts back one character
    - get_lexeme(): Returns current lexeme
    - reset_lexeme_begin(): Marks new lexeme start
    """
    
    def __init__(self, buffer_manager: BufferManager, 
                 sync_method: SyncMethod = SyncMethod.SEMAPHORE):
        """
        Initialize the character stream.
        
        Args:
            buffer_manager: BufferManager instance
            sync_method: Synchronization method for threaded reader
        """
        self.buffer_manager = buffer_manager
        self.sync_method = sync_method
        self.reader = create_threaded_reader(buffer_manager, sync_method)
        
        # Pointers
        self.forward = 0           # Current scanning position
        self.forward_buffer = 0    # Which buffer forward is in
        self.lexeme_begin = 0      # Start of current lexeme
        self.lexeme_begin_buffer = 0  # Which buffer lexeme_begin is in
        
        # Track if we've started processing
        self.started = False
        self.first_buffer_ready = False
        
        # Characters that span buffer boundary (for lexeme extraction)
        self.lexeme_parts: List[str] = []
        
        # Statistics
        self.chars_read = 0
        self.buffer_transitions = []
        
        # EOF flag
        self._eof = False
        
    def open(self, file_path: str):
        """
        Open a file for reading.
        
        Args:
            file_path: Path to source file
        """
        self.buffer_manager.reset()
        self.reader.start_reading(file_path)
        
        self.forward = 0
        self.forward_buffer = 0
        self.lexeme_begin = 0
        self.lexeme_begin_buffer = 0
        self.lexeme_parts = []
        self.chars_read = 0
        self.buffer_transitions = []
        self._eof = False
        self.started = True
        self.first_buffer_ready = False
        
        # Wait for first buffer to be filled
        self._wait_for_first_buffer()
    
    def _wait_for_first_buffer(self):
        """Wait for the first buffer to be ready."""
        timeout = 5.0
        start = time.time()
        
        while time.time() - start < timeout:
            if self.buffer_manager.is_buffer_ready(0):
                self.buffer_manager.mark_buffer_processing(0)
                self.first_buffer_ready = True
                return
            if self.buffer_manager.is_eof():
                self._eof = True
                return
            time.sleep(0.01)
        
        raise TimeoutError("Timeout waiting for first buffer")
    
    def get_next_char(self) -> str:
        """
        Get the next character from input.
        
        Returns:
            Next character, or empty string if EOF
        """
        if self._eof and not self._has_more_content():
            return ''
        
        # Get character at current position
        char = self.buffer_manager.get_char_at(self.forward_buffer, self.forward)
        
        # Check for sentinel (end of buffer content)
        if char == SENTINEL:
            # Try to switch to next buffer
            if self._handle_buffer_transition():
                # Successfully switched, get char from new buffer
                char = self.buffer_manager.get_char_at(self.forward_buffer, self.forward)
                if char == SENTINEL:
                    # Still sentinel means EOF
                    self._eof = True
                    return ''
            else:
                # No more buffers available
                self._eof = True
                return ''
        
        # Move forward pointer
        self.forward += 1
        self.chars_read += 1
        self.buffer_manager.total_chars_processed = self.chars_read
        
        return char
    
    def _has_more_content(self) -> bool:
        """Check if there's more content to read."""
        # Check current buffer
        current_pos = self.forward
        current_buf = self.forward_buffer
        
        if current_pos < self.buffer_manager.get_content_length(current_buf):
            return True
        
        # Check other buffer
        other_buf = 1 - current_buf
        if self.buffer_manager.is_buffer_ready(other_buf):
            return True
        
        return False
    
    def _handle_buffer_transition(self) -> bool:
        """
        Handle transition from one buffer to another.
        
        Returns:
            True if transition successful, False if no more data
        """
        old_buffer = self.forward_buffer
        new_buffer = 1 - old_buffer
        
        # Record transition for demo
        self.buffer_transitions.append({
            'from_buffer': old_buffer,
            'to_buffer': new_buffer,
            'position': self.chars_read,
            'time': time.time()
        })
        
        # Wait for new buffer to be ready
        timeout = 2.0
        start = time.time()
        
        while time.time() - start < timeout:
            if self.buffer_manager.is_buffer_ready(new_buffer):
                break
            if self.buffer_manager.is_eof():
                # Check if new buffer has content
                if not self.buffer_manager.is_buffer_ready(new_buffer):
                    return False
                break
            time.sleep(0.001)
        else:
            # Timeout - check EOF
            if self.buffer_manager.is_eof():
                return False
            return False
        
        # Release old buffer for refilling (only if lexeme doesn't span)
        if self.lexeme_begin_buffer != old_buffer:
            if isinstance(self.reader, ThreadedReaderSemaphore):
                self.reader.release_buffer(old_buffer)
            else:
                self.reader.release_buffer(old_buffer)
        else:
            # Lexeme spans buffers - save the part from old buffer
            lexeme_part = self._extract_from_buffer(
                old_buffer, 
                self.lexeme_begin, 
                self.buffer_manager.get_content_length(old_buffer)
            )
            if lexeme_part:
                self.lexeme_parts.append(lexeme_part)
            
            # Now release old buffer
            if isinstance(self.reader, ThreadedReaderSemaphore):
                self.reader.release_buffer(old_buffer)
            else:
                self.reader.release_buffer(old_buffer)
            
            # Update lexeme_begin to start of new buffer
            self.lexeme_begin = 0
            self.lexeme_begin_buffer = new_buffer
        
        # Switch to new buffer
        self.forward_buffer = new_buffer
        self.forward = 0
        self.buffer_manager.mark_buffer_processing(new_buffer)
        
        # Increment buffer switch counter
        with self.buffer_manager.lock:
            self.buffer_manager.buffer_switches += 1
        
        return True
    
    def _extract_from_buffer(self, buffer_idx: int, start: int, end: int) -> str:
        """Extract string from buffer between positions."""
        chars = []
        for i in range(start, min(end, self.buffer_manager.buffer_size)):
            char = self.buffer_manager.get_char_at(buffer_idx, i)
            if char == SENTINEL:
                break
            chars.append(char)
        return ''.join(chars)
    
    def unget_char(self):
        """
        Put back one character (move forward pointer back).
        
        Note: Cannot unget across buffer boundary after buffer was released.
        """
        if self.forward > 0:
            self.forward -= 1
            self.chars_read -= 1
        elif self.forward == 0 and len(self.lexeme_parts) > 0:
            # Can't truly unget across released buffer
            # This is a limitation noted in documentation
            raise RuntimeError("Cannot unget across buffer boundary after buffer release")
    
    def get_lexeme(self) -> str:
        """
        Get the current lexeme (from lexeme_begin to forward).
        
        Returns:
            String containing the current lexeme
        """
        # If lexeme spans multiple buffers, combine parts
        if self.lexeme_parts:
            parts = self.lexeme_parts.copy()
            # Add current buffer portion
            current_part = self._extract_from_buffer(
                self.forward_buffer,
                self.lexeme_begin if self.lexeme_begin_buffer == self.forward_buffer else 0,
                self.forward
            )
            parts.append(current_part)
            return ''.join(parts)
        else:
            # Lexeme is within single buffer
            return self._extract_from_buffer(
                self.forward_buffer,
                self.lexeme_begin,
                self.forward
            )
    
    def reset_lexeme_begin(self):
        """
        Mark the start of a new lexeme at current forward position.
        """
        # Clear any saved lexeme parts
        self.lexeme_parts = []
        
        # Set lexeme_begin to current forward position
        self.lexeme_begin = self.forward
        self.lexeme_begin_buffer = self.forward_buffer
    
    def peek_char(self) -> str:
        """
        Peek at the next character without advancing.
        
        Returns:
            Next character or empty string if EOF
        """
        char = self.get_next_char()
        if char:
            self.unget_char()
        return char
    
    def is_eof(self) -> bool:
        """Check if end of file reached."""
        return self._eof and not self._has_more_content()
    
    def close(self):
        """Close the character stream and cleanup."""
        self.reader.stop()
        self.started = False
    
    def get_position(self) -> Tuple[int, int, int]:
        """
        Get current position info.
        
        Returns:
            Tuple of (total_chars_read, current_buffer, position_in_buffer)
        """
        return (self.chars_read, self.forward_buffer, self.forward)
    
    def get_statistics(self) -> dict:
        """Get stream statistics."""
        reader_stats = self.reader.get_statistics()
        buffer_stats = self.buffer_manager.get_statistics()
        
        return {
            'chars_read': self.chars_read,
            'buffer_transitions': len(self.buffer_transitions),
            'transition_details': self.buffer_transitions,
            'reader': reader_stats,
            'buffer_manager': buffer_stats
        }
    
    def get_transition_demo(self, num_chars: int = 5) -> List[dict]:
        """
        Get demo of buffer transitions showing characters around transition points.
        
        Args:
            num_chars: Number of characters to show before/after transition
            
        Returns:
            List of transition info with surrounding characters
        """
        # This is mainly for demonstration purposes
        # In practice, we'd need to save characters around transitions
        demo = []
        for transition in self.buffer_transitions:
            demo.append({
                'position': transition['position'],
                'from_buffer': transition['from_buffer'],
                'to_buffer': transition['to_buffer']
            })
        return demo


class SimpleCharacterStream:
    """
    Simple single-buffer character stream for comparison.
    No threading, just sequential reading.
    """
    
    def __init__(self, buffer_size: int = 4096):
        self.buffer_size = buffer_size
        self.buffer = []
        self.position = 0
        self.lexeme_begin = 0
        self.file_handle = None
        self._eof = False
        self.chars_read = 0
        self.buffer_refills = 0
        self.refill_times = []
    
    def open(self, file_path: str):
        """Open file for reading."""
        self.file_handle = open(file_path, 'r', encoding='utf-8', errors='replace')
        self.buffer = []
        self.position = 0
        self.lexeme_begin = 0
        self._eof = False
        self.chars_read = 0
        self.buffer_refills = 0
        self.refill_times = []
        self._refill_buffer()
    
    def _refill_buffer(self):
        """Refill buffer from file."""
        if self._eof or self.file_handle is None:
            return
        
        start_time = time.perf_counter()
        content = self.file_handle.read(self.buffer_size)
        refill_time = time.perf_counter() - start_time
        
        if not content:
            self._eof = True
            return
        
        self.buffer = list(content)
        self.position = 0
        self.buffer_refills += 1
        self.refill_times.append(refill_time)
    
    def get_next_char(self) -> str:
        """Get next character."""
        if self.position >= len(self.buffer):
            if self._eof:
                return ''
            self._refill_buffer()
            if self._eof or self.position >= len(self.buffer):
                return ''
        
        char = self.buffer[self.position]
        self.position += 1
        self.chars_read += 1
        return char
    
    def unget_char(self):
        """Put back one character."""
        if self.position > 0:
            self.position -= 1
            self.chars_read -= 1
    
    def get_lexeme(self) -> str:
        """Get current lexeme."""
        return ''.join(self.buffer[self.lexeme_begin:self.position])
    
    def reset_lexeme_begin(self):
        """Reset lexeme begin to current position."""
        self.lexeme_begin = self.position
    
    def is_eof(self) -> bool:
        """Check if EOF reached."""
        return self._eof and self.position >= len(self.buffer)
    
    def close(self):
        """Close the stream."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def get_statistics(self) -> dict:
        """Get statistics."""
        avg_refill = sum(self.refill_times) / len(self.refill_times) if self.refill_times else 0
        return {
            'chars_read': self.chars_read,
            'buffer_refills': self.buffer_refills,
            'average_refill_time_ms': avg_refill * 1000,
            'buffer_size': self.buffer_size
        }


if __name__ == "__main__":
    import os
    
    print("Testing CharacterStream...")
    
    # Create test file
    test_content = "Hello World! This is a test. " * 100
    test_file = "test_stream.tmp"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Test double-buffered stream
        bm = BufferManager(buffer_size=50)
        stream = CharacterStream(bm, SyncMethod.SEMAPHORE)
        
        stream.open(test_file)
        
        # Read some characters
        chars = []
        for _ in range(100):
            char = stream.get_next_char()
            if not char:
                break
            chars.append(char)
        
        print(f"Read: {''.join(chars[:50])}...")
        print(f"Position: {stream.get_position()}")
        print(f"Statistics: {stream.get_statistics()}")
        
        stream.close()
        
        # Test simple stream
        print("\nTesting SimpleCharacterStream...")
        simple = SimpleCharacterStream(buffer_size=50)
        simple.open(test_file)
        
        chars = []
        for _ in range(100):
            char = simple.get_next_char()
            if not char:
                break
            chars.append(char)
        
        print(f"Read: {''.join(chars[:50])}...")
        print(f"Statistics: {simple.get_statistics()}")
        
        simple.close()
        
    finally:
        os.remove(test_file)
    
    print("\nTest completed!")
