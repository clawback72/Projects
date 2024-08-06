import sys
import yfinance as yf
import pandas as pd
import argparse
from datetime import date, timedelta

def main():

    # initialize default variables
    today = date.today()
    t_delta = int(30)
    ticker_2 = "SPY"
    investment = float(1000)

    # argparse parameters and make adjustments to defaults
    parser = argparse.ArgumentParser(
        description = "Returns basic security information, P/E ratio, price performance, and present value of a given investment for the inquiry term",
            )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("ticker", help = "ticker of security for primary inquiry")
    parser.add_argument("-c", "--c", help = "ticker of secondary security for comparison - default SPY")
    parser.add_argument("-i", "--i", type = float, help = "specify initial investment amount - default $1,000")
    group.add_argument("-d", "--d", type = int, help = "specify time for performance calculation in days - default 30")
    group.add_argument("-y", "--y", type = float, help = "specify time for performance calcualtion in years - may use float values for fractional years")
    args = parser.parse_args()

    if args.c:
        ticker_2 = args.c.upper()
    if args.i:
        investment = float(args.i)
    if args.d:
        t_delta = int(args.d)
    if args.y:
        t_delta = int(args.y * 365.25)

    timediff = timedelta(days=-t_delta)
    startdate = today + timediff

    # get ticker information for required fields
    ticker_1 = args.ticker.upper()
    info_1 = get_info(ticker_1)
    isin_1 = get_isin(ticker_1)

    #ticker_2 = input("Ticker 2: ").upper()
    info_2 = get_info(ticker_2)
    isin_2 = get_isin(ticker_2)

    # get price data for tickers
    price_info = get_prices(ticker_1 + " " + ticker_2, startdate, today, t_delta)

    # unpack price values for correct ticker variables / extract date and flag values
    if ticker_1 == price_info["ticker1"][0]:
        stdt, t1sp, eddt, t1ep, f1, f2 = price_info["ticker1"][1], price_info["ticker1"][2],price_info["ticker1"][3], price_info["ticker1"][4],price_info["ticker1"][5],price_info["ticker1"][6]
        t2sp, t2ep = price_info["ticker2"][2], price_info["ticker2"][4]

    elif ticker_1 == price_info["ticker2"][0]:
        stdt, t1sp, eddt, t1ep, f1, f2 = price_info["ticker2"][1], price_info["ticker2"][2],price_info["ticker2"][3], price_info["ticker2"][4],price_info["ticker2"][5],price_info["ticker2"][6]
        t2sp, t2ep = price_info["ticker1"][2], price_info["ticker1"][4]

    # get returns for both tickers
    ret1 = get_return(t1sp, t1ep)
    ret2 = get_return(t2sp, t2ep)

    # get PV of investment using price return
    inv1 = get_invest(ret1, investment)
    inv2 = get_invest(ret2, investment)

    # assemble data for printing
    print_table = [
        ["Ticker:", ticker_1, ticker_2],
        ["ISIN:", isin_1, isin_2],
        ["Industry:", info_1["industry"], info_2["industry"]],
        ["Name:", info_1["longName"], info_2["longName"]],
        ["Address:", info_1["address1"], info_2["address1"]],
        ["", info_1["city"]+" "+info_1["state"]+"  "+info_1["zip"], info_2["city"]+" "+info_2["state"]+"  "+info_2["zip"]],
        ["Website:", info_1["website"], info_2["website"]],
        ["","",""],
        ["Trailing P/E ratio:", str(info_1["trailingPE"]), str(info_2["trailingPE"])],
        ["","",""],
        [stdt+" closing price:", str(t1sp), str(t2sp)],
        [eddt+" closing price:", str(t1ep), str(t2ep)],
        ["Price Growth:", str(round(ret1*100,4))+"%", str(round(ret2 * 100,4))+"%"],
        [f"PV of ${investment:,.2f}"+" investment:", f"${inv1:,.2f}", f"${inv2:,.2f}"]
    ]

    print()

    # set column width based on longest word in print table
    colw = max(len(word) for row in print_table for word in row) + 1

    # print formatted print table left justified
    for row in print_table:
        print(" ".join(word.ljust(colw) for word in row))

    if f1 != "None":
        print("\n" f"*{startdate} specified as start date - using first concurrent close price date {stdt}")
    if f2 != "None":
        print("\n" f"*most recent concurrent close date is {eddt}")

    print()

def get_info(t):
    try:
        stock = yf.Ticker(t)
        raw_info = stock.info
        info = {}
    except:
        sys.exit(f"No data available for ticker {t}")

    # set list of keys to return
    keys = ["symbol", "longName", "address1", "city", "state", "zip", "industry", "website", "trailingPE"]

    # get values only for keys defined and return
    info = {key: raw_info.get(key) for key in keys}

    # replace "None" values with ""
    for _ in info:
        if info[_] is None:
            info[_] = ""

    # add comma after city value
    if info["city"] != "":
        info["city"] += ","

    # add N/A to trailingPE for securities that have no earnings
    if info["trailingPE"] == "":
        info["trailingPE"] = "N/A"

    return info

def get_isin(t):
    stock = yf.Ticker(t)
    isin = stock.isin
    return isin

def get_prices(t, strtd, edd, term):

    #retrieve price table for ticker pair
    if term < 366:
        data = yf.download(t, start=strtd, end=edd, progress=False)
    else:
        data = yf.download(t, start=strtd, end=edd, period = "1mo", progress=False)

    # set default variables
    flag = "None"
    flag2 = "None"
    s1sp = 0
    s1ep = 0

    # get clean tickers from the headers column
    # yfinance alphabetizes price columns by tickers so we need to know which price is which on return from function
    headers = list(data.columns)
    s1t = clean_header(headers[0])
    s2t = clean_header(headers[1])

    # get first common start date / start prices
    for i in range(len(data)):
        if not pd.isna(data.iloc[i,2]):
            s1sp = round(data.iloc[i,2],2)
            sd = data.index[i].strftime('%Y-%m-%d')
        if pd.isna(data.iloc[i,2]):
            flag = "s1sp"
        if not pd.isna(data.iloc[i,3]) and s1sp > 0:
            s2sp = round(data.iloc[i,3],2)
            break
        if pd.isna(data.iloc[i,3]):
            flag = "s2sp"

    # get last common end date / end prices
    for i in range(len(data)):
        if not pd.isna(data.iloc[-i,2]) and i != 0:
            s1ep = round(data.iloc[-i,2],2)
            ed = data.index[-i].strftime('%Y-%m-%d')
        if pd.isna(data.iloc[-i,2]) and i != 0:
            flag2 = "s1ep"
        if not pd.isna(data.iloc[-i,3]) and s1ep > 0:
            s2ep = round(data.iloc[-i,3],2)
            break
        if pd.isna(data.iloc[-i,3]) and i != 0:
            flag2 = "s2ep"

    # create dictionary for value return
    price_info = {"ticker1": [s1t, sd, s1sp, ed, s1ep, flag, flag2],
                    "ticker2": [s2t, sd, s2sp, ed, s2ep, flag, flag2]}

    return price_info

def clean_header(t):
    clean = t[1]
    return clean

def get_return(s_price, e_price):
    s_return = (e_price - s_price) / s_price
    return s_return

def get_invest(ret, inv):
    inv_new = round(inv * (1 + ret),2)
    return inv_new

if __name__ == "__main__":
    main()