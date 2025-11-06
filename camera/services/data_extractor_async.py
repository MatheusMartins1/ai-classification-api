import asyncio
import concurrent.futures
from typing import Dict, Any, Optional
import time
import datetime
import threading

from camera.services.data_extractor import DataExtractorService
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="image_data_extractor_async",
    filename=None,
    dir_name=None,
    prefix="data_extractor_async",
    level_name="ERROR",
)


class AsyncDataExtractor:
    def __init__(self, _camera):
        self._camera = _camera
        
        # Thread pool lifecycle management
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._executor_lock = threading.Lock()
        self._max_workers = 4  # Calibrate based on camera SDK capabilities
        self._is_initialized = False
        
        # Timeout management based on camera rate
        self._timeout_multiplier = 0.95  # Use 90% of frame time as timeout
        self._default_timeout = 10.0  # Default 2s timeout for safety (increased from 0.1s)
        self._validation_timeout = 10.0  # Longer timeout for validation operations

    def _get_or_create_executor(self) -> concurrent.futures.ThreadPoolExecutor:
        """
        Get or create ThreadPoolExecutor with proper lifecycle management.
        Thread-safe singleton pattern for executor management.
        
        Returns:
            concurrent.futures.ThreadPoolExecutor: Reusable thread pool executor
        """
        if self._executor is None:
            with self._executor_lock:
                if self._executor is None:  # Double-check locking
                    self._executor = concurrent.futures.ThreadPoolExecutor(
                        max_workers=self._max_workers,
                        thread_name_prefix="AsyncDataExtractor"
                    )
                    self._is_initialized = True
                    logger.info(f"ThreadPoolExecutor created with {self._max_workers} workers")
        
        return self._executor
    
    def shutdown_executor(self) -> None:
        """
        Shutdown the ThreadPoolExecutor properly.
        Should be called when the service is being stopped.
        """
        with self._executor_lock:
            if self._executor is not None:
                self._executor.shutdown(wait=True)
                self._executor = None
                self._is_initialized = False
                logger.info("ThreadPoolExecutor shutdown completed")
    
    def _calculate_timeout(self, is_validation: bool = False) -> float:
        """
        Calculate timeout based on camera rate formula: frequency_seconds = 1.0 / fps.
        Uses _timeout_multiplier to ensure extraction completes within frame time.
        
        Args:
            is_validation (bool): If True, use longer timeout for validation operations
        
        Returns:
            float: Timeout in seconds for each data extraction
        """
        if is_validation:
            return self._validation_timeout
            
        if self._camera and hasattr(self._camera, 'fps') and self._camera.fps:
            frequency_seconds = 1.0 / self._camera.fps
            timeout = frequency_seconds * self._timeout_multiplier
            return max(timeout, self._default_timeout)  # Ensure minimum timeout
        
        return self._default_timeout

    async def extract_all_data_types_parallel(self, data_types: list, is_validation: bool = False) -> Dict[str, Any]:
        """
        Extract all data types in parallel with timeout control based on camera rate.
        
        Args:
            data_types (list): List of data types to extract
            is_validation (bool): If True, use longer timeout for validation operations
            
        Returns:
            Dict[str, Any]: Combined thermal data from all extractions
        """
        # Calculate timeout based on camera fps and operation type
        timeout = self._calculate_timeout(is_validation=is_validation)
        
        # Create tasks for each data type with deduplication
        unique_data_types = list(dict.fromkeys(data_types))  # Remove duplicates preserving order
        tasks = []
        for data_type in unique_data_types:
            task = self._extract_single_data_type_async(data_type)
            tasks.append(task)

        # Execute all tasks in parallel with timeout
        start_time = time.time()
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Data extraction timed out after {timeout:.3f}s (camera rate based)")
            # Cancel pending tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Return partial results that completed
            results = [task.result() if task.done() and not task.cancelled() else None for task in tasks]
        
        end_time = time.time()
        extraction_time = end_time - start_time
        
        logger.debug(f"Async extraction completed in {extraction_time:.3f}s (timeout: {timeout:.3f}s)")

        # Process results with timeout and error handling
        thermal_data_dict = {"data_keys": [], "imageData": {}}

        for i, result in enumerate(results):
            data_type = unique_data_types[i] if i < len(unique_data_types) else f"unknown_{i}"
            
            # Handle various result types (None, Exception, valid data)
            if result is None:
                logger.warning(f"No result for {data_type} (likely timeout or cancellation)")
                continue
            elif isinstance(result, Exception):
                logger.error(f"Error extracting {data_type}: {result}")
                continue

            # Process valid thermal data
            if result and "imageData" in result and "data" in result["imageData"]:
                data_dict = result["imageData"]["data"]
                if data_dict:
                    for data_key in data_dict.keys():
                        thermal_data_dict["data_keys"].append(data_key)
                        thermal_data_dict["imageData"][data_key] = data_dict[data_key]

        return thermal_data_dict

    async def _extract_single_data_type_async(self, data_type: str) -> Dict[str, Any]:
        """
        Extract a single data type asynchronously using the reusable thread pool.
        
        Args:
            data_type (str): Type of thermal data to extract
            
        Returns:
            Dict[str, Any]: Extracted thermal data
        """
        # Get the reusable ThreadPoolExecutor
        executor = self._get_or_create_executor()
        
        # Use the persistent executor instead of creating new ones
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            DataExtractorService.get_thermal_data_for_view,
            self._camera,
            data_type,
        )

        return result
    
    async def extract_single_data_type_validation(self, data_type: str) -> Dict[str, Any]:
        """
        Extract a single data type for validation purposes with extended timeout.
        
        Args:
            data_type (str): Type of thermal data to extract
            
        Returns:
            Dict[str, Any]: Extracted thermal data or None if failed
        """
        try:
            # Get the reusable ThreadPoolExecutor
            executor = self._get_or_create_executor()
            
            # Use longer timeout for validation
            timeout = self._validation_timeout
            
            # Use the persistent executor with extended timeout
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    executor,
                    DataExtractorService.get_thermal_data_for_view,
                    self._camera,
                    data_type,
                ),
                timeout=timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"Validation timeout for data type '{data_type}' after {self._validation_timeout}s")
            return None
        except Exception as e:
            logger.error(f"Validation error for data type '{data_type}': {e}")
            return None
    
    def update_camera(self, camera) -> None:
        """
        Update the camera instance.
        
        Args:
            camera: New camera instance
        """
        self._camera = camera
        logger.info("Camera updated in AsyncDataExtractor")
    
    def get_timeout_info(self) -> Dict[str, float]:
        """
        Get current timeout configuration info.
        
        Returns:
            Dict[str, float]: Timeout information
        """
        timeout = self._calculate_timeout()
        fps = self._camera.fps if self._camera and hasattr(self._camera, 'fps') else None
        
        return {
            "current_timeout": timeout,
            "camera_fps": fps,
            "timeout_multiplier": self._timeout_multiplier,
            "default_timeout": self._default_timeout,
            "frequency_seconds": 1.0 / fps if fps else None
        }


"""
# Usage example:
async def process_data_types_async(self):
    extractor = AsyncDataExtractor(self._camera)
    
    # Extract data with automatic timeout management
    thermal_data_dict = await extractor.extract_all_data_types_parallel(
        self._data_to_extract
    )
    
    # Get timeout info for debugging
    timeout_info = extractor.get_timeout_info()
    logger.debug(f"Extraction timeout info: {timeout_info}")
    
    return thermal_data_dict
"""
