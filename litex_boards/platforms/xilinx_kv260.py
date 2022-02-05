#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer


_io = [
    ("fan", 0, Pins("A12"), IOStandard("LVCMOS33")),
]


class Platform(XilinxPlatform):
    def __init__(self):
        XilinxPlatform.__init__(self, "xck26-sfvc784-2lv-c", _io, toolchain="vivado")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]", ]

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment, *args, **kwargs):
        XilinxPlatform.do_finalize(self, fragment, *args, **kwargs)
