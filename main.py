import asyncio
import csv
import json
import requests
import config
from loguru import logger
import random


class Checker:
    def __init__(self, wallet, prox):
        self.wallet = wallet.lower()
        self.proxies = prox
    async def check(self):
        for _ in range(5):
            try:
                url = f"https://www.zksyncpepe.com/resources/amounts/{self.wallet}.json"
                random_proxy = random.choice(self.proxies)
                proxies = {"http":random_proxy, } if self.proxies else None
                result = requests.get(url=url, proxies=proxies)

                if result.status_code == 200:
                    try:
                        drop = json.loads(result.text)[0]
                        print(f"{self.wallet} | {drop}")
                        return self.wallet, drop
                    except json.decoder.JSONDecodeError:
                        print(f"{self.wallet} | Дроп 0 {proxies}")
                        return self.wallet, 0
                else:
                    print(f"Failed with status code: {result.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

        return self.wallet, 0


async def write_to_csv(wallet, drop):
    with open('result.csv', 'a', newline='') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(['wallet', 'drop'])

        writer.writerow([wallet, drop])


async def main():
    with open("wallets.txt", "r") as f:
        wallets = [row.strip() for row in f]

    with open("proxy.txt", "r") as file:
        prox = [row.strip() for row in file]

    batches = [wallets[i:i + config.amount_wallets_in_batch] for i in range(0, len(wallets), config.amount_wallets_in_batch)]

    for batch in batches:
        tasks = []
        for wallet in batch:
            checker1 = Checker(wallet, prox)
            tasks.append(checker1.check())

        res = await asyncio.gather(*tasks)
        for res_ in res:
            wallet, drop= res_
            await write_to_csv(wallet, drop)

        tasks = []


if __name__ == '__main__':
    results = asyncio.run(main())
    logger.success(f'Парам..парам...пам...ВСЕ!!!')
