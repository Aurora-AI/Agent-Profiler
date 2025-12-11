import asyncio
import time
import httpx
import statistics

async def run_benchmark():
    url = "http://localhost:8000/generate"
    payload = {
        "provider_name": "mock",
        "prompt": "Benchmark",
        "config": {
            "response_delay": 0.1, # Simulate 100ms backend latency
            "mock_response": "Bench"
        }
    }

    # Increase concurrency to stress test the async loop
    concurrency = 100
    total_requests = 1000

    async with httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=concurrency, max_connections=concurrency)) as client:
        # Warmup
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"Warmup failed: {e}")
            return

        print("Starting Benchmark...")
        start_time = time.time()
        latencies = []

        sem = asyncio.Semaphore(concurrency)

        async def request_worker():
            async with sem:
                req_start = time.time()
                try:
                    resp = await client.post(url, json=payload, timeout=30.0)
                    resp.raise_for_status()
                    latencies.append(time.time() - req_start)
                except Exception as e:
                    print(f"Error: {e}")

        tasks = [request_worker() for _ in range(total_requests)]
        await asyncio.gather(*tasks)

        total_time = time.time() - start_time

    throughput = total_requests / total_time
    avg_latency = statistics.mean(latencies) if latencies else 0
    p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else avg_latency

    print(f"Total Time: {total_time:.2f}s")
    print(f"Requests: {total_requests}")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Avg Latency: {avg_latency*1000:.2f} ms")
    print(f"P95 Latency: {p95_latency*1000:.2f} ms")

    return throughput, avg_latency

if __name__ == "__main__":
    asyncio.run(run_benchmark())
