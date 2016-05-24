from telex.plugin import TelexPlugin
from urllib import request
from urllib import error
import json


class BTCPlugin(TelexPlugin):
    """
    Retrieve BTC prices
    """
    patterns = [
        "^{prefix}btc$",
        "^{prefix}btc ([Ee][Uu][Rr])$",
        "^{prefix}btc ([Uu][Ss][Dd])$",
        "^{prefix}btc (EUR) (\d+[\d.]*)$",
        "^{prefix}btc (USD) (\d+[\d.]*)$",
        ]

    usage = [
        "!btc [EUR|USD] [amount]"
    ]

    def run(self, msg, matches):
        cur = 'USD'
        amt = None

        if matches.group(0) == "{prefix}btc".format(prefix=self.bot.pfx):
            return self.get_btcx(cur, amt)

        cur = matches.group(1).upper()
        if len(matches.groups()) == 2:
            amt = matches.group(2)

        return self.get_btcx(cur, amt)

    def get_btcx(self, currency, amount):
        try:
            base_url = 'https://api.bitcoinaverage.com/ticker/global'
            resp = request.urlopen("{0}/{1}".format(base_url, currency))
        except error.HTTPError:
            return None

        data = json.loads(resp.read().decode('utf-8'))
        text = "BTC/{0}\nBuy: {1}\nSell: {2}".format(currency, data['ask'],
                                                               data['bid'])

        if amount is not None:
            btc = float(amount) / float(data['ask'])
            text = text + "\n{0} {1} = BTC {2}".format(currency, amount, btc)

        return text
