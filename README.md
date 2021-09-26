# custom-etf

Build a custom ETF using [`aiorobinhood`](https://github.com/omikader/aiorobinhood).

# Usage

Save your Robinhood credentials in an `.ini` file, e.g.

```
[credentials]
username=foo
password=bar
```

Run with `--help` to see all of the options.

```bash
$ python3 -m venv /tmp/my_venv
$ source /tmp/my_venv/bin/activate
(my_venv) $ pip install -r requirements.txt
...
(my_venv) $ python etf.py --help
usage: etf.py [-h] [-d] [-e EPSILON] [-p PATH] [-t TIMEOUT] [-w {cap,equal,file}] SSSS [SSSS ...]

Rebalance your Robinhood stock portfolio.

positional arguments:
  SSSS                  list of space separated stock symbols

optional arguments:
  -h, --help            show this help message and exit
  -d, --dry-run         disables live ordering (default: False)
  -e EPSILON, --epsilon EPSILON
                        minimum difference to trigger a rebalance (in dollars) (default: 0.01)
  -p PATH, --path PATH  path to the config file (default: /Users/omikader/.config.ini)
  -t TIMEOUT, --timeout TIMEOUT
                        aiorobinhood request timeout (default: 3)
  -w {cap,equal,file}, --weighting {cap,equal,file}
                        weighting scheme to use for rebalancing (default: equal)
```

# Example

```bash
(my_venv) $ python etf.py AAPL ABNB ABT AMAT AMD AMZN BLK BRK.B BYND CMG COST CRM CRWD DDOG DOCU DPZ ETSY GOOG HD LULU LRCX MRNA MSCI MSFT NET NFLX NOW NVDA OKTA PAYC PINS PYPL QCOM RGEN RNG ROKU SBUX SHOP SNOW SPGI SPOT SQ TMO TSLA TTD TWLO UNH WING ZM ZS
Enter the sms code: 123456
+ AAPL  $4.38
- ABNB  $16.96
+ ABT   $9.73
- AMAT  $55.64
- AMD   $5.48
- AMZN  $6.68
+ BLK   $29.88
- BRK.B $2.98
+ BYND  $71.76
- CMG   $11.53
- COST  $2.20
- CRM   $18.40
+ CRWD  $4.59
- DDOG  $27.83
+ DOCU  $4.22
- DPZ   $5.25
- ETSY  $26.13
- GOOG  $13.16
- HD    $20.07
- LRCX  $28.91
- LULU  $21.24
+ MRNA  $31.52
- MSCI  $2.42
- MSFT  $34.72
- NET   $43.31
+ NFLX  $25.06
- NOW   $15.03
+ NVDA  $3.99
+ OKTA  $18.81
- PAYC  $13.88
+ PINS  $20.72
+ PYPL  $5.37
+ QCOM  $37.51
- RGEN  $27.08
- RNG   $9.46
+ ROKU  $39.62
+ SBUX  $45.06
+ SHOP  $18.47
- SNOW  $8.59
- SPGI  $9.95
+ SPOT  $45.29
- SQ    $26.91
+ TMO   $18.27
- TSLA  $10.02
- TTD   $0.14
+ TWLO  $1.31
- UNH   $42.32
- WING  $17.94
+ ZM    $93.98
- ZS    $0.21
```

# File Example

Create a JSON file with symbols and corresponding allocations, e.g.

```JSON
{
  "FB": 0.25,
  "AAPL": 0.10,
  "AMZN": 0.55,
  "NFLX": 0.05,
  "GOOG": 0.05
}
```

Run using `-w file` mode:

```bash
(my_venv) $ python etf.py -w file symbols.json
```

# Dependencies

- Python 3.7+
- [aiorobinhood](https://pypi.org/project/aiorobinhood/)
