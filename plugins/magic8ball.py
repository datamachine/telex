from telex.plugin import TelexPlugin
from random import randrange
import sys

class Magic8BallPlugin(TelexPlugin):
    """
    It's a magic eight ball!
    """

    patterns = ["^{prefix}8ball (.*)"]
    usage = ["{prefix}8ball <question>"]
    

    def __init__(self):
        super().__init__()

        self.responses = [
                "Maybe", 
                "Probably", 
                "Yes", 
                "No", 
                "In you're dreams", 
                "Not Likely", 
                "That could be the case", 
                "Absolutely", 
                "Most definitely", 
                "No way",
                "Try Again.",
                "Most definitely not",
                "I'm not feeling it.. ask me again"
            ]
        
    def run(self, msg, matches):
        bad_qwords = ["who", "what", "where", "when", "why", "how"]
        first_word = matches.group(1).lower().split()[0]

        try:
            if first_word in bad_qwords:
                return "Those are questions I'm not sure how to answer. Perhaps you can ask Google."
            else:
                return self.responses[randrange(len(self.responses))]
        except:
            return sys.exc_info()[0]
