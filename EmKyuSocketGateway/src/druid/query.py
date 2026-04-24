import datetime
from typing import Any

from pydruid.client import *
from pydruid.client import PyDruid

from env import DRUID_URI


class PyDruidClient:
    _CLIENT = PyDruid(DRUID_URI, "druid/v2")

    def getCurrentRealData(self) -> Any:
        current = datetime.datetime.now()
        return {
            "trades": self._CLIENT.timeseries(
                datasource="trades",
                granularity="day",
                intervals="2025-02-02/p4w",
            ),
            "oderbook": self._CLIENT.timeseries(
                datasource="orderbook",
                granularity="day",
                intervals="2025-02-02/p4w",
            ),
        }

    def getCurrentSynthData(self) -> Any:
        return {"trades_fake": "", "orderbook_fake": ""}

    def getCurrentData(self) -> Any:
        realRegistry = self.getCurrentRealData()
        synthRegistry = self.getCurrentSynthData()
        return {"real": realRegistry, "fake": synthRegistry}
