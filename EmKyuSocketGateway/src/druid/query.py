from typing import Any

from pydruid.client import *
from pydruid.client import PyDruid
from pydruid.utils.aggregators import doublesum
from pydruid.utils.filters import Dimension
from pydruid.utils.postaggregator import Field


class PyDruidClient:
    _CLIENT = PyDruid("", "druid/v2")

    def getCurrentSynthData(self) -> Any:
        return self._CLIENT.timeseries(
            datasource="twitterstream",
            granularity="day",
            intervals="2014-02-02/p4w",
            aggregations={
                "length": doublesum("tweet_length"),
                "count": doublesum("count"),
            },
            post_aggregations={"avg_tweet_length": (Field("length") / Field("count"))},
            filter=Dimension("first_hashtag") == "sochi2014",
        )
