"""
Multi-Threaded Reader for Double Buffering
Week 2: CC Lab - Double Buffering Using Multi-Threading

This module implements producer-consumer pattern with both
semaphores and condition variables for synchronization.
"""

import threading
import time
from typing import Optional, Callable
from enum import Enum
from buffer_manager import BufferManager, BufferState, SENTINEL


class SyncMethod(Enum):
    """Synchronization method for producer-consumer."""
    SEMAPHORE = "semaphore"
    CONDITION_VARIABLE = "condition_variable"


class ThreadedReaderSemaphore:
    """
    Multi-threaded file reader using semaphores for synchronization.
    
    Producer (Reader Thread): Reads file chunks into buffers
    Consumer (Scanner Thread): Processes characters from buffers
    """
    
    def __init__(self, buffer_manager: BufferManager):
        """
        Initialize the threaded reader with semaphores.
        
        Args:
            buffer_manager: BufferManager instance to use
        """
        self.buffer_manager = buffer_manager
        
        # Semaphores for synchronization
        # empty_sem: counts empty buffers available (initially 2)
        # full_sem: counts full buffers available (initially 0)
        self.empty_sem = threading.Semaphore(2)
        self.full_sem = threading.Semaphore(0)
        
        # Mutex for critical sections
        self.mutex = threading.Lock()
        
        # Stop signal
        self.stop_event = threading.Event()
        
        # Reader thread
        self.reader_thread: Optional[threading.Thread] = None
        
        # File handle
        self.file_path: Optional[str] = None
        self.file_handle = None
        
        # Statistics
        self.fill_times = []
        self.total_bytes_read = 0
        self.read_operations = 0
        
        # Which buffer to fill next
        self.next_fill_buffer = 0
        
    def start_reading(self, file_path: str):
        """
        Start reading file in background thread.
        
        Args:
            file_path: Path to file to read
        """
        self.file_path = file_path
        self.stop_event.clear()
        self.buffer_manager.reset()
        
        # Reset semaphores
        # Drain any excess permits
        while self.full_sem.acquire(blocking=False):
            pass
        # Reset empty semaphores (should have 2)
        self.empty_sem = threading.Semaphore(2)
        self.full_sem = threading.Semaphore(0)
        
        self.next_fill_buffer = 0
        self.fill_times = []
        self.total_bytes_read = 0
        self.read_operations = 0
        
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()
    
    def _reader_loop(self):
        """Reader thread main loop - produces filled buffers."""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                self.file_handle = f
                
                while not self.stop_event.is_set():
                    # Wait for an empty buffer
                    if not self.empty_sem.acquire(timeout=0.1):
                        continue
                    
                    if self.stop_event.is_set():
                        break
                    
                    # Determine which buffer to fill
                    with self.mutex:
                        buffer_idx = self.next_fill_buffer
                        self.next_fill_buffer = 1 - self.next_fill_buffer
                    
                    # Read from file
                    start_time = time.perf_counter()
                    content = f.read(self.buffer_manager.buffer_size)
                    fill_time = time.perf_counter() - start_time
                    
                    if not content:
                        # EOF reached
                        self.buffer_manager.set_eof()
                        self.full_sem.release()  # Signal that we're done
                        break
                    
                    # Fill the buffer
                    bytes_written = self.buffer_manager.fill_buffer(buffer_idx, content)
                    
                    # Update statistics
                    self.fill_times.append(fill_time)
                    self.total_bytes_read += bytes_written
                    self.read_operations += 1
                    
                    # Signal that a buffer is full
                    self.full_sem.release()
                    
        except Exception as e:
            print(f"Reader thread error: {e}")
            self.buffer_manager.set_eof()
            self.full_sem.release()
    
    def wait_for_buffer(self, timeout: float = 1.0) -> bool:
        """
        Wait for a buffer to be filled.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if buffer available, False if timeout or EOF
        """
        if self.buffer_manager.is_eof():
            # Check if current buffer still has content
            active = self.buffer_manager.get_active_buffer_index()
            if self.buffer_manager.get_buffer_state(active) == BufferState.FULL:
                return True
            return False
        
        return self.full_sem.acquire(timeout=timeout)
    
    def release_buffer(self, buffer_idx: int):
        """
        Signal that a buffer has been processed and is ready for refill.
        
        Args:
            buffer_idx: Index of buffer that was processed
        """
        self.buffer_manager.mark_buffer_empty(buffer_idx)
        self.empty_sem.release()
    
    def stop(self):
        """Stop the reader thread."""
        self.stop_event.set()
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2.0)
    
    def get_statistics(self) -> dict:
        """Get reading statistics."""
        avg_fill_time = sum(self.fill_times) / len(self.fill_times) if self.fill_times else 0
        return {
            'total_bytes_read': self.total_bytes_read,
            'read_operations': self.read_operations,
            'average_fill_time_ms': avg_fill_time * 1000,
            'fill_times': self.fill_times.copy()
        }


class ThreadedReaderCondVar:
    """
    Multi-threaded file reader using condition variables for synchronization.
    
    This implementation uses mutex + condition variable instead of semaphores.
    """
    
    def __init__(self, buffer_manager: BufferManager):
        """
        Initialize the threaded reader with condition variables.
        
        Args:
            buffer_manager: BufferManager instance to use
        """
        self.buffer_manager = buffer_manager
        
        # Condition variable and lock
        self.lock = threading.Lock()
        self.buffer_available = threading.Condition(self.lock)
        self.buffer_empty = threading.Condition(self.lock)
        
        # Buffer states for CV-based tracking
        self.buffers_filled = [False, False]
        self.buffers_processed = [True, True]  # Initially both are "processed" (ready to fill)
        
        # Stop signal
        self.stop_event = threading.Event()
        
        # Reader thread
        self.reader_thread: Optional[threading.Thread] = None
        
        # File info
        self.file_path: Optional[str] = None
        
        # Statistics
        self.fill_times = []
        self.total_bytes_read = 0
        self.read_operations = 0
        
        # Which buffer to fill next
        self.next_fill_buffer = 0
        
    def start_reading(self, file_path: str):
        """Start reading file in background thread."""
        self.file_path = file_path
        self.stop_event.clear()
        self.buffer_manager.reset()
        
        with self.lock:
            self.buffers_filled = [False, False]
            self.buffers_processed = [True, True]
        
        self.next_fill_buffer = 0
        self.fill_times = []
        self.total_bytes_read = 0
        self.read_operations = 0
        
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()
    
    def _reader_loop(self):
        """Reader thread main loop using condition variables."""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                while not self.stop_event.is_set():
                    buffer_idx = None
                    
                    # Wait for an empty buffer
                    with self.buffer_empty:
                        while not self.stop_event.is_set():
                            # Find a processed (empty) buffer
                            for i in range(2):
                                if self.buffers_processed[i] and not self.buffers_filled[i]:
                                    buffer_idx = i
                                    break
                            
                            if buffer_idx is not None:
                                self.buffers_processed[buffer_idx] = False
                                break
                            
                            # Wait for notification
                            self.buffer_empty.wait(timeout=0.1)
                    
                    if self.stop_event.is_set() or buffer_idx is None:
                        break
                    
                    # Read from file
                    start_time = time.perf_counter()
                    content = f.read(self.buffer_manager.buffer_size)
                    fill_time = time.perf_counter() - start_time
                    
                    if not content:
                        # EOF reached
                        self.buffer_manager.set_eof()
                        with self.buffer_available:
                            self.buffer_available.notify_all()
                        break
                    
                    # Fill the buffer
                    bytes_written = self.buffer_manager.fill_buffer(buffer_idx, content)
                    
                    # Update statistics
                    self.fill_times.append(fill_time)
                    self.total_bytes_read += bytes_written
                    self.read_operations += 1
                    
                    # Signal that buffer is filled
                    with self.buffer_available:
                        self.buffers_filled[buffer_idx] = True
                        self.buffer_available.notify_all()
                    
        except Exception as e:
            print(f"Reader thread error: {e}")
            self.buffer_manager.set_eof()
            with self.buffer_available:
                self.buffer_available.notify_all()
    
    def wait_for_buffer(self, buffer_idx: int, timeout: float = 1.0) -> bool:
        """
        Wait for a specific buffer to be filled.
        
        Args:
            buffer_idx: Buffer index to wait for
            timeout: Maximum wait time
            
        Returns:
            True if buffer is ready, False otherwise
        """
        with self.buffer_available:
            start = time.time()
            while not self.buffers_filled[buffer_idx]:
                if self.buffer_manager.is_eof():
                    return False
                remaining = timeout - (time.time() - start)
                if remaining <= 0:
                    return False
                self.buffer_available.wait(timeout=remaining)
            return True
    
    def wait_for_any_buffer(self, timeout: float = 1.0) -> Optional[int]:
        """
        Wait for any buffer to be filled.
        
        Returns:
            Index of filled buffer, or None if timeout/EOF
        """
        if self.buffer_manager.is_eof():
            return None
            
        with self.buffer_available:
            start = time.time()
            while True:
                for i in range(2):
                    if self.buffers_filled[i]:
                        return i
                
                if self.buffer_manager.is_eof():
                    return None
                    
                remaining = timeout - (time.time() - start)
                if remaining <= 0:
                    return None
                self.buffer_available.wait(timeout=remaining)
    
    def release_buffer(self, buffer_idx: int):
        """Signal that a buffer has been processed."""
        self.buffer_manager.mark_buffer_empty(buffer_idx)
        with self.buffer_empty:
            self.buffers_filled[buffer_idx] = False
            self.buffers_processed[buffer_idx] = True
            self.buffer_empty.notify_all()
    
    def stop(self):
        """Stop the reader thread."""
        self.stop_event.set()
        with self.buffer_available:
            self.buffer_available.notify_all()
        with self.buffer_empty:
            self.buffer_empty.notify_all()
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2.0)
    
    def get_statistics(self) -> dict:
        """Get reading statistics."""
        avg_fill_time = sum(self.fill_times) / len(self.fill_times) if self.fill_times else 0
        return {
            'total_bytes_read': self.total_bytes_read,
            'read_operations': self.read_operations,
            'average_fill_time_ms': avg_fill_time * 1000,
            'fill_times': self.fill_times.copy()
        }


def create_threaded_reader(buffer_manager: BufferManager, 
                           sync_method: SyncMethod = SyncMethod.SEMAPHORE):
    """
    Factory function to create a threaded reader with specified sync method.
    
    Args:
        buffer_manager: BufferManager to use
        sync_method: Synchronization method (SEMAPHORE or CONDITION_VARIABLE)
        
    Returns:
        ThreadedReader instance (either Semaphore or CondVar based)
    """
    if sync_method == SyncMethod.SEMAPHORE:
        return ThreadedReaderSemaphore(buffer_manager)
    else:
        return ThreadedReaderCondVar(buffer_manager)


if __name__ == "__main__":
    # Simple test
    import os
    
    print("Testing ThreadedReader with Semaphores...")
    
    # Create a test file
    test_content = "Hello World! " * 1000
    test_file = "test_reader.tmp"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        bm = BufferManager(buffer_size=100)
        reader = ThreadedReaderSemaphore(bm)
        
        reader.start_reading(test_file)
        time.sleep(0.5)  # Let reader fill buffers
        
        print(f"Statistics: {reader.get_statistics()}")
        print(f"Buffer stats: {bm.get_statistics()}")
        
        reader.stop()
        
    finally:
        os.remove(test_file)
    
    print("\nTest completed!")
