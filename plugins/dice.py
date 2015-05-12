import plugintypes
import re
import random

class DicePlugin(plugintypes.TelegramPlugin):
    """
    Roll Dice
    """
    DEFAULT_SIDES = 100
    DEFAULT_NUMBER_OF_DICE = 1
    MAX_NUMBER_OF_DICE = 100


    patterns = [
        "^!roll (.*)"
    ]

    usage = [
        "!roll d<sides>[+modifier]|<count>d<sides>[+modifier]",
    ]

    def run(self, msg, matches):
        dice = matches.group(1).split("+")
        total = 0

        text = ""

        for die in dice:
            try:
                total += int(die)          # add raw value
            except ValueError:             # we probably have a die specification
                m = re.search("(\d*)d(\d+)", die)
                if m is None:
                    return "Bad dice specification."

                my_total = 0
                num_dice = 1
                if m.group(1) != '':
                    num_dice = int(m.group(1))
                num_dice = min(num_dice, self.MAX_NUMBER_OF_DICE)
                sides = int(m.group(2))

                fmt = "{{0:0{0}}}".format(sides)
                results = ""

                for i in range(num_dice):
                    result = random.randint(1, sides)
                    my_total += result
                    results += "{0:02d} ".format(result)

                text += "Rolling {num}d{sides}: (subtotal: {total})\n{results}\n".format(num=num_dice, sides=sides,
                                                                                         total=my_total, results=results)
                total += my_total

        text += "Grand Total: {total}".format(total=total)

        return text