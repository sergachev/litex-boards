#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *

from litex_boards.platforms import digilent_zedboard
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys,      sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq, with_led_chaser=True, **kwargs):
        platform = digilent_zedboard.Platform()

        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs['integrated_sram_size'] = 0
            kwargs['with_uart'] = False
            self.mem_map = {
                'csr': 0x4000_0000,  # Zynq GP0 default
            }

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Zedboard",
            ident_version  = True,
            **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            self.cpu.set_ps7(name="Zynq",
                             preset="ZedBoard",
                             config={'PCW_FPGA0_PERIPHERAL_FREQMHZ': sys_clk_freq / 1e6})

            # Connect AXI GP0 to the SoC
            wb_gp0 = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map['csr'])
            self.add_wb_master(wb_gp0)

            self.bus.add_region("sram", SoCRegion(
                origin=self.mem_map["sram"],
                size=512 * 1024 * 1024)
            )
            self.bus.add_region("rom", SoCRegion(
                origin=self.mem_map["rom"],
                size=32 * 1024 * 1024,
                linker=True)
            )
            use_ps7_clk = True
        else:
            use_ps7_clk = False

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Zedboard")
    parser.add_argument("--build",        action="store_true", help="Build bitstream")
    parser.add_argument("--load",         action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq", default=100e6,       help="System clock frequency (default: %(default)d)")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    parser.set_defaults(cpu_type="zynq7000")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    print(builder.compile_software)
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"), device=1)


if __name__ == "__main__":
    main()
