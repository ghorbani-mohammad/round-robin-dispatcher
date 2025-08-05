import asyncio
import aiohttp
import json
import time


async def send_request(session: aiohttp.ClientSession, request_id: str, payload: dict):
    """Send a single request to the API"""
    url = "http://localhost:8000/process-request"
    data = {"request_id": request_id, "payload": payload}

    try:
        async with session.post(url, json=data) as response:
            result = await response.json()
            print(f"Request {request_id}: Status {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
    except Exception as e:
        print(f"Error sending request {request_id}: {e}")
        return None


async def test_round_robin_and_deduplication():
    """Test the round-robin assignment and deduplication features"""
    print("=== Testing Round-Robin Load Balancer and Deduplication ===\n")

    async with aiohttp.ClientSession() as session:
        # Test 1: Send 5 unique requests to see round-robin in action
        print("Test 1: Sending 5 unique requests to test round-robin distribution")
        print("-" * 60)

        # Send requests SEQUENTIALLY to test round-robin properly
        results = []
        for i in range(5):
            request_id = f"test_request_{i+1}"
            payload = {"data": f"test data {i+1}", "timestamp": time.time()}
            result = await send_request(session, request_id, payload)
            results.append(result)
            # Small delay to ensure SEQUENTIAL processing
            await asyncio.sleep(0.1)

        print(f"\nWorker assignments from responses:")
        for i, result in enumerate(results):
            if result and "worker_id" in result:
                print(f"Request {i+1}: Worker {result['worker_id']}")

        # Test 2: Test deduplication by sending duplicate requests
        print(f"\n\nTest 2: Testing deduplication - sending duplicate requests")
        print("-" * 60)

        # Try to send the same request again
        await send_request(
            session, "test_request_1", {"data": "duplicate attempt"}
        )

        # Making sure all requests are processed
        await asyncio.sleep(10)


async def test_concurrent_requests():
    """Test sending many CONCURRENT requests"""
    print(f"\n\n=== Testing Concurrent Requests ===\n")

    async with aiohttp.ClientSession() as session:
        # Send 10 requests simultaneously
        tasks = []
        for i in range(10):
            request_id = f"concurrent_test_{i+1}"
            payload = {"batch": "concurrent", "request_num": i + 1}
            task = send_request(session, request_id, payload)
            tasks.append(task)

        # Send all at once
        results = await asyncio.gather(*tasks)

        # Show worker distribution
        worker_counts = {}
        for result in results:
            if result and "worker_id" in result:
                worker_id = result["worker_id"]
                worker_counts[worker_id] = worker_counts.get(worker_id, 0) + 1

        print(f"\nConcurrent requests distribution:")
        for worker_id, count in worker_counts.items():
            print(f"Worker {worker_id}: {count} requests")


if __name__ == "__main__":
    print("Starting tests...")

    # Run tests
    asyncio.run(test_round_robin_and_deduplication())
    asyncio.run(test_concurrent_requests())
