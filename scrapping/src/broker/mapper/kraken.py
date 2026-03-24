from broker.mapper.model.time_series_cripto import TSData


class KrakenDataMapper:
    @staticmethod
    def mapResponse(data):
        return TSData(
            timestamp=data['data'][0]['timestamp'],
            name=data["data"][0]['symbol'],
            price=data["data"][0]['bid'],
            volume=data["data"][0]['volume'],
        )
