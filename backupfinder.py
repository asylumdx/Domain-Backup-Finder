import asyncio
import httpx
import argparse
from tqdm import tqdm
import sys

CONCURRENCY_LIMIT = 40  
BATCH_SIZE = 1000  
FILE_EXTENSIONS = [".zip", ".sql", ".tar.gz"] 
MIN_FILE_SIZE = 1 * 1024 * 1024  

async def check_url(client, url, results):
    try:
        response = await client.head(url, timeout=5)
        status_code = response.status_code
        headers = response.headers

        if status_code == 200:
            content_length = headers.get('Content-Length', '0')

            if int(content_length) > MIN_FILE_SIZE:
                results.append(url)
                print(f"{url} - Exists")
                sys.stdout.flush() 
    except Exception as e:
        pass

async def process_url(client, semaphore, url, results, progress_bar):
    async with semaphore:
        await check_url(client, url, results)
        progress_bar.update(1) 

async def process_batch(client, semaphore, urls_batch, results, progress_bar):
    tasks = []
    for url in urls_batch:
        task = process_url(client, semaphore, url, results, progress_bar)
        tasks.append(task)
    await asyncio.gather(*tasks)

async def check_urls(input_file, output_file):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    results = []

    with open(input_file, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]

    total_urls = len(domains) * len(FILE_EXTENSIONS) * 2 

    async with httpx.AsyncClient() as client:
        with tqdm(total=total_urls, desc="Checking URLs", unit="URL") as progress_bar:
            for i in range(0, len(domains), BATCH_SIZE):
                urls_batch = []
                batch = domains[i:i + BATCH_SIZE]

                for domain in batch:
                    domain_name = domain.split('.')[0]  

                    for ext in FILE_EXTENSIONS:
                        urls_batch.append(f"https://{domain}/{domain}{ext}")
                        urls_batch.append(f"https://{domain}/{domain_name}{ext}")

                await process_batch(client, semaphore, urls_batch, results, progress_bar)

    with open(output_file, 'w') as f:
        for url in results:
            f.write(f"{url}\n")
        print(f"\nResults saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Check URL Backup Existence.")
    parser.add_argument("input_file", help="Input file containing domain names")
    parser.add_argument("output_file", help="Output file to save existing URLs")
    
    args = parser.parse_args()
    asyncio.run(check_urls(args.input_file, args.output_file))

if __name__ == "__main__":
    main()
