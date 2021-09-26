#!/usr/bin/env python3

import argparse
import asyncio
import configparser
import json
import logging
import os
import sys

from aiorobinhood import RobinhoodClient, ClientError


async def main(args: argparse.Namespace) -> None:
    # Load Robinhood account credentials
    config = configparser.ConfigParser(interpolation=None)
    config.read(args.path)

    # Define symbols set
    if args.weighting == "file":
        try:
            with open(args.symbols) as f:
                weights = json.load(f)
                if sum(weights.values()) > 1:
                    raise ValueError("Sum of custom weights must not exceed 1")
                symbols = set(weights.keys())
        except OSError:
            raise RuntimeError(f"Could not find file '{args.symbols}'")
        except json.JSONDecodeError:
            raise RuntimeError(f"'{args.symbols}' does not contain valid JSON")
    else:
        symbols = set(args.symbols)

    async with RobinhoodClient(timeout=args.timeout) as client:
        await client.login(**config["credentials"])
        portfolio, fundamentals, positions = await asyncio.gather(
            client.get_portfolio(),
            client.get_fundamentals(symbols=symbols),
            client.get_positions(),
        )

        # Compute the target equity for each security
        total_equity = 0.99 * float(portfolio["equity"])
        if args.weighting == "cap":
            total_cap = sum(float(f["market_cap"]) for f in fundamentals)
            equity = {
                symbol: total_equity * float(f["market_cap"]) / total_cap
                for symbol, f in zip(symbols, fundamentals)
            }
        elif args.weighting == "equal":
            equity = dict.fromkeys(symbols, total_equity / len(symbols))
        elif args.weighting == "file":
            equity = {
                symbol: total_equity * weight
                for symbol, weight in weights.items()
            }

        # Rebalance our existing positions
        sell_orders = []
        buy_orders = []
        for position, quote in zip(
            positions,
            await client.get_quotes(instruments=[p["instrument"] for p in positions]),
        ):
            if position["instrument"] != quote["instrument"]:
                raise RuntimeError("Position and quote data are not aligned!")

            symbol = quote["symbol"]
            quantity = float(position["quantity"])

            if symbol not in symbols:
                logging.info(f"- {symbol:<5} (closing position)")
                sell_orders.append(client.place_market_sell_order(symbol, quantity=quantity))
            else:
                current_equity = quantity * float(quote["last_trade_price"])
                target_equity = equity[symbol]
                if current_equity - target_equity > args.epsilon:
                    sell_value = current_equity - target_equity
                    logging.info(f"- {symbol:<5} ${sell_value:0.2f}")
                    sell_orders.append(client.place_market_sell_order(symbol, amount=sell_value))
                elif target_equity - current_equity > args.epsilon:
                    buy_value = target_equity - current_equity
                    logging.info(f"+ {symbol:<5} ${buy_value:0.2f}")
                    buy_orders.append(client.place_market_buy_order(symbol, amount=buy_value))
                else:
                    logging.info(f"= {symbol:<5} |${current_equity - target_equity:0.2f}| < ${args.epsilon}")

                symbols.remove(symbol)

        # Add new stocks to our positions
        for symbol in symbols:
            logging.info(f"+ {symbol:<5} ${equity[symbol]:0.2f} (new position)")
            buy_orders.append(client.place_market_buy_order(symbol, amount=equity[symbol]))

        # Process the orders (sell orders first)
        for order in sell_orders + buy_orders:
            if args.dry_run:
                # Cancel the coroutine
                order.close()
            else:
                try:
                    await order
                except ClientError:
                    symbol = order.cr_frame.f_locals["args"][1]
                    logging.exception(f"{symbol} order failed")
                finally:
                    await asyncio.sleep(6)

        await client.logout()


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    file_mode = "file" in sys.argv
    
    parser = argparse.ArgumentParser(
        description="Rebalance your Robinhood stock portfolio.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "symbols",
        metavar="SSSS",
        type=str,
        nargs=None if file_mode else "+",
        help="path to JSON symbols file" if file_mode else "list of space separated stock symbols",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="disables live ordering",
    )
    parser.add_argument(
        "-e",
        "--epsilon",
        type=float,
        default=0.01,
        help="minimum difference to trigger a rebalance (in dollars)",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=f"{os.getenv('HOME')}/.config.ini",
        help="path to the config file",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=3,
        help="aiorobinhood request timeout",
    )
    parser.add_argument(
        "-w",
        "--weighting",
        type=str,
        choices=["cap", "equal", "file"],
        default="equal",
        help="weighting scheme to use for rebalancing",
    )

    asyncio.run(main(parser.parse_args()))
