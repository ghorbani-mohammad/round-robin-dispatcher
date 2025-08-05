import random
import asyncio
import threading
from typing import Dict
from datetime import datetime

from sqlalchemy.orm import Session

from models import ProcessedRequest
from cache import request_cache


class WorkerManager:
    def __init__(self, num_workers: int = 3):
        self.num_workers = num_workers
        self.current_worker = 0
        self.lock = threading.Lock()
        self.worker_status = {i: "free" for i in range(num_workers)}

    def get_next_worker(self) -> int:
        """Get next worker ID using round-robin algorithm"""
        with self.lock:
            worker_id = self.current_worker
            self.current_worker = (self.current_worker + 1) % self.num_workers
            return worker_id

    def set_worker_busy(self, worker_id: int):
        """Mark worker as busy"""
        with self.lock:
            self.worker_status[worker_id] = "busy"

    def set_worker_free(self, worker_id: int):
        """Mark worker as free"""
        with self.lock:
            self.worker_status[worker_id] = "free"

    def get_worker_status(self) -> Dict[int, str]:
        """Get current status of all workers"""
        with self.lock:
            return self.worker_status.copy()

    async def process_request(self, db: Session, request_record: ProcessedRequest):
        """Simulate processing a request with a worker"""
        worker_id = request_record.worker_id

        # Log that worker has started processing
        print(f"Worker {worker_id} started request {request_record.request_id}")

        try:
            # Mark worker as busy
            self.set_worker_busy(worker_id)
            db.commit()

            # Update cache with new status
            cache_data = {
                "worker_id": request_record.worker_id,
                "created_at": request_record.created_at.isoformat(),
                "payload": request_record.get_payload(),
            }
            request_cache.set(request_record.request_id, cache_data)

            # Simulate work (1-10 seconds)
            processing_time = random.randint(1, 10)
            await asyncio.sleep(processing_time)

            # fill the result with useful information
            result = {
                "processed_by": f"worker_{worker_id}",
                "processing_time": processing_time,
                "processed_at": datetime.utcnow().isoformat(),
                "original_payload": request_record.get_payload(),
                "result": f"Successfully processed request {request_record.request_id}",
            }

            # Update request with result
            request_record.set_result(result)
            db.commit()

            # Update cache with completion status
            cache_data = {
                "worker_id": request_record.worker_id,
                "created_at": request_record.created_at.isoformat(),
                "payload": request_record.get_payload(),
                "result": result,
            }
            request_cache.set(request_record.request_id, cache_data)

            print(f"Worker {worker_id} completed request {request_record.request_id}")

        except Exception as e:
            # Handle processing error
            request_record.set_result({"error": str(e)})
            db.commit()

            # Update cache with failure status
            cache_data = {
                "worker_id": request_record.worker_id,
                "created_at": request_record.created_at.isoformat(),
                "payload": request_record.get_payload(),
                "error": str(e),
            }
            request_cache.set(request_record.request_id, cache_data)

            print(
                f"Worker {worker_id} failed to process request {request_record.request_id}: {e}"
            )

        finally:
            # Mark worker as free
            self.set_worker_free(worker_id)


# Global worker manager instance
worker_manager = WorkerManager(num_workers=3)
