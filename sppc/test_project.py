import yfinance as yf
import pandas as pd
from project import get_info
from project import get_isin
from project import get_return
from project import get_invest
import pytest

def main():
    test_get_info()
    test_get_isin()
    test_get_return()
    test_get_invest()

def test_get_info():
    with pytest.raises(SystemExit):
        get_info("nnnnn")
        get_info("ticker")
        get_info("123")

def test_get_isin():
    assert get_isin("MSFT") == "-"
    assert get_isin("AAPL") == "US0378331005"
    assert get_isin("V") == "US92826C8394"

def test_get_return():
    assert get_return(100,110) == .1
    assert get_return(100,90) == -0.1
    assert get_return(100,150) == .5
    assert get_return(100,0) == -1

def test_get_invest():
    assert get_invest(.5, 1000) == 1500
    assert get_invest(-.5, 1000) == 500
    assert get_invest(1, 2500) == 5000
    assert get_invest(-.75, 2000) == 500
    
if __name__ == "__main__":
    main()