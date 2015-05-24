import plugintypes
from urllib import request, error, parse


class CalculatorPlugin(plugintypes.TelegramPlugin):
    """
    Calculator that uses mathjs to evaluate
    """
    patterns = [
        "^!calc (.*)$",
        ]

    usage = [
        "!calc expression: evaluates the expression and sends the result.",
    ]

    def run(self, msg, matches):
        return self.mathjs(matches.group(1))

    def mathjs(self, expr):
        try:
            base_url = 'http://api.mathjs.org/v1'
            resp = request.urlopen("{0}/?expr={1}".format(base_url,
                parse.quote_plus(expr)))
        except error.HTTPError as err:
            if err.code == 400:
                return err.read().decode('utf-8')
            else:
                return "Unexpected error\nIs api.mathjs.org up?"

        text = 'Result: ' + resp.read().decode('utf-8')

        return text
