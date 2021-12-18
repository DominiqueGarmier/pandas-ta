# -*- coding: utf-8 -*-
from pandas import DataFrame, Series
from pandas_ta import Imports
from pandas_ta.overlap import ma
from pandas_ta.utils import get_offset, verify_series, get_drift, zero


def dm(high: Series, low: Series, length: int = None, mamode: str = None, talib: bool = None, drift: int = None,
       offset: int = None, **kwargs) -> DataFrame:
    """Directional Movement (DM)

    The Directional Movement was developed by J. Welles Wilder in 1978 attempts to
    determine which direction the price of an asset is moving. It compares prior
    highs and lows to yield to two series +DM and -DM.

    Sources:
        https://www.tradingview.com/pine-script-reference/#fun_dmi
        https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=24&Name=Directional_Movement_Index

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        mamode (str): See ```help(ta.ma)```.  Default: 'rma'
        talib (bool): If TA Lib is installed and talib is True, Returns the TA Lib
            version. Default: True
        drift (int): The difference period. Default: 1
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        fill_method (value, optional): Type of fill method

    Returns:
        pd.DataFrame: DMP (+DM) and DMN (-DM) columns.
    """
    # Validate Arguments
    length = int(length) if length and length > 0 else 14
    mamode = mamode.lower() if mamode and isinstance(mamode, str) else "rma"
    high = verify_series(high)
    low = verify_series(low)
    drift = get_drift(drift)
    offset = get_offset(offset)
    mode_tal = bool(talib) if isinstance(talib, bool) else True

    if high is None or low is None:
        return

    if Imports["talib"] and mode_tal:
        from talib import MINUS_DM, PLUS_DM
        pos = PLUS_DM(high, low, length)
        neg = MINUS_DM(high, low, length)
    else:
        up = high - high.shift(drift)
        dn = low.shift(drift) - low

        pos_ = ((up > dn) & (up > 0)) * up
        neg_ = ((dn > up) & (dn > 0)) * dn

        pos_ = pos_.apply(zero)
        neg_ = neg_.apply(zero)

        # Not the same values as TA Lib's -+DM (Good First Issue)
        pos = ma(mamode, pos_, length=length)
        neg = ma(mamode, neg_, length=length)

    # Offset
    if offset != 0:
        pos = pos.shift(offset)
        neg = neg.shift(offset)

    _params = f"_{length}"
    data = {
        f"DMP{_params}": pos,
        f"DMN{_params}": neg,
    }

    dmdf = DataFrame(data)
    # print(dmdf.head(20))
    # print()
    dmdf.name = f"DM{_params}"
    dmdf.category = "trend"

    return dmdf
