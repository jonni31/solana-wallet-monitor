#!/usr/bin/env python3
"""Solana Wallet Monitor."""
import asyncio, json, argparse
from datetime import datetime
import websockets, httpx

SOLANA_WS = "wss://api.mainnet-beta.solana.com"

class WalletMonitor:
    def __init__(self, wallet, webhook=None):
        self.wallet, self.webhook = wallet, webhook

    async def subscribe(self):
        async with websockets.connect(SOLANA_WS) as ws:
            sub = {"jsonrpc":"2.0","id":1,"method":"accountSubscribe","params":[self.wallet,{"encoding":"jsonParsed","commitment":"confirmed"}]}
            await ws.send(json.dumps(sub))
            await ws.recv()
            print(f"[+] Subscribed to {self.wallet}")
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=30)
                    data = json.loads(msg)
                    if "params" in data:
                        val = data["params"].get("result",{}).get("value",{})
                        sol = val.get("lamports",0)/1e9
                        print(f"[TX] {datetime.utcnow().isoformat()} | {sol:.4f} SOL")
                except asyncio.TimeoutError:
                    await ws.ping()
                except Exception as e:
                    print(f"[!] {e}"); break

async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--wallet", required=True)
    p.add_argument("--webhook")
    a = p.parse_args()
    m = WalletMonitor(a.wallet, a.webhook)
    while True:
        try: await m.subscribe()
        except: await asyncio.sleep(5)

if __name__ == "__main__": asyncio.run(main())
