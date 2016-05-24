# -*- coding: utf8 -*-
from telex.plugin import TelexPlugin


class EmoticonsPlugin(TelexPlugin):
    patterns = {
        "^{prefix}lod": "lod",
        "^{prefix}lolidk": "lolidk"
    }

    usage = [
        "{prefix}lod, {prefix}lolidk",
    ]

    def lod(self, msg, matches):
        """
        ಠ_ಠ
        """
        return b'\xe0\xb2\xa0_\xe0\xb2\xa0'

    def lolidk(self, msg, matches):
        """
        ¯\_(ツ)_/¯
        """
        return b'\xc2\xaf\\_(\xe3\x83\x84)_/\xc2\xaf'
