#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Ilia Sergachev <ilia@sergachev.ch>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *

from litex_boards.platforms import xilinx_kv260
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.build.tools import write_to_file

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps") | self.rst)
        else:
            self.submodules.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(platform.request(platform.default_clk_name), platform.default_clk_freq)
            pll.create_clkout(self.cd_sys,      sys_clk_freq)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    mem_map = {"csr": 0xA000_0000}  # default GP0 address on ZynqMP

    def __init__(self, sys_clk_freq, **kwargs):
        platform = xilinx_kv260.Platform()

        if kwargs.get("cpu_type", None) == "zynqmp":
            kwargs['integrated_sram_size'] = 0

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on KV260",
            **kwargs)

        # ZynqMP Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynqmp":
            self.cpu.config.update({
                'PSU_MIO_36_DIRECTION': 'out',
                'PSU_MIO_37_DIRECTION': 'in',
                'PSU__UART1__BAUD_RATE': 115200,
                'PSU__CRL_APB__UART1_REF_CTRL__DIVISOR0': 10,
            })
            # generated from board xml presets
            self.cpu.config.update({
                'PSU_BANK_0_IO_STANDARD': 'LVCMOS18',
                'PSU_BANK_1_IO_STANDARD': 'LVCMOS18',
                'PSU_BANK_2_IO_STANDARD': 'LVCMOS18',
                'PSU_BANK_3_IO_STANDARD': 'LVCMOS18',
                'PSU_MIO_0_DRIVE_STRENGTH': '4',
                'PSU_MIO_0_SLEW': 'slow',
                'PSU_MIO_10_DRIVE_STRENGTH': '4',
                'PSU_MIO_10_SLEW': 'slow',
                'PSU_MIO_11_DRIVE_STRENGTH': '4',
                'PSU_MIO_11_SLEW': 'slow',
                'PSU_MIO_12_DRIVE_STRENGTH': '4',
                'PSU_MIO_12_SLEW': 'slow',
                'PSU_MIO_13_DRIVE_STRENGTH': '4',
                'PSU_MIO_13_SLEW': 'slow',
                'PSU_MIO_14_DRIVE_STRENGTH': '4',
                'PSU_MIO_14_SLEW': 'slow',
                'PSU_MIO_15_DRIVE_STRENGTH': '4',
                'PSU_MIO_15_SLEW': 'slow',
                'PSU_MIO_16_DRIVE_STRENGTH': '4',
                'PSU_MIO_16_SLEW': 'slow',
                'PSU_MIO_17_DRIVE_STRENGTH': '4',
                'PSU_MIO_17_SLEW': 'slow',
                'PSU_MIO_18_DRIVE_STRENGTH': '4',
                'PSU_MIO_18_SLEW': 'slow',
                'PSU_MIO_19_DRIVE_STRENGTH': '4',
                'PSU_MIO_19_SLEW': 'slow',
                'PSU_MIO_1_DRIVE_STRENGTH': '4',
                'PSU_MIO_1_SLEW': 'slow',
                'PSU_MIO_20_DRIVE_STRENGTH': '4',
                'PSU_MIO_20_SLEW': 'slow',
                'PSU_MIO_21_DRIVE_STRENGTH': '4',
                'PSU_MIO_21_SLEW': 'slow',
                'PSU_MIO_22_DRIVE_STRENGTH': '4',
                'PSU_MIO_22_SLEW': 'slow',
                'PSU_MIO_23_DRIVE_STRENGTH': '4',
                'PSU_MIO_23_SLEW': 'slow',
                'PSU_MIO_24_DRIVE_STRENGTH': '4',
                'PSU_MIO_24_SLEW': 'slow',
                'PSU_MIO_25_DRIVE_STRENGTH': '4',
                'PSU_MIO_25_SLEW': 'slow',
                'PSU_MIO_27_DRIVE_STRENGTH': '4',
                'PSU_MIO_27_SLEW': 'slow',
                'PSU_MIO_29_DRIVE_STRENGTH': '4',
                'PSU_MIO_29_SLEW': 'slow',
                'PSU_MIO_2_DRIVE_STRENGTH': '4',
                'PSU_MIO_2_SLEW': 'slow',
                'PSU_MIO_32_DRIVE_STRENGTH': '4',
                'PSU_MIO_32_SLEW': 'slow',
                'PSU_MIO_33_DRIVE_STRENGTH': '4',
                'PSU_MIO_33_SLEW': 'slow',
                'PSU_MIO_34_DIRECTION': 'inout',
                'PSU_MIO_34_DRIVE_STRENGTH': '4',
                'PSU_MIO_34_SLEW': 'slow',
                'PSU_MIO_35_DRIVE_STRENGTH': '4',
                'PSU_MIO_35_SLEW': 'slow',
                'PSU_MIO_36_DRIVE_STRENGTH': '4',
                'PSU_MIO_36_SLEW': 'slow',
                'PSU_MIO_38_DRIVE_STRENGTH': '4',
                'PSU_MIO_38_SLEW': 'slow',
                'PSU_MIO_39_DRIVE_STRENGTH': '4',
                'PSU_MIO_39_SLEW': 'slow',
                'PSU_MIO_3_DRIVE_STRENGTH': '4',
                'PSU_MIO_3_SLEW': 'slow',
                'PSU_MIO_40_DRIVE_STRENGTH': '4',
                'PSU_MIO_40_SLEW': 'slow',
                'PSU_MIO_41_DRIVE_STRENGTH': '4',
                'PSU_MIO_41_SLEW': 'slow',
                'PSU_MIO_42_DRIVE_STRENGTH': '4',
                'PSU_MIO_42_SLEW': 'slow',
                'PSU_MIO_43_DIRECTION': 'inout',
                'PSU_MIO_43_DRIVE_STRENGTH': '4',
                'PSU_MIO_43_SLEW': 'slow',
                'PSU_MIO_44_DIRECTION': 'inout',
                'PSU_MIO_44_DRIVE_STRENGTH': '4',
                'PSU_MIO_44_SLEW': 'slow',
                'PSU_MIO_46_DRIVE_STRENGTH': '4',
                'PSU_MIO_46_SLEW': 'slow',
                'PSU_MIO_47_DRIVE_STRENGTH': '4',
                'PSU_MIO_47_SLEW': 'slow',
                'PSU_MIO_48_DRIVE_STRENGTH': '4',
                'PSU_MIO_48_SLEW': 'slow',
                'PSU_MIO_49_DRIVE_STRENGTH': '4',
                'PSU_MIO_49_SLEW': 'slow',
                'PSU_MIO_4_DRIVE_STRENGTH': '4',
                'PSU_MIO_4_SLEW': 'slow',
                'PSU_MIO_50_DRIVE_STRENGTH': '4',
                'PSU_MIO_50_SLEW': 'slow',
                'PSU_MIO_51_DRIVE_STRENGTH': '4',
                'PSU_MIO_51_SLEW': 'slow',
                'PSU_MIO_54_DRIVE_STRENGTH': '4',
                'PSU_MIO_54_SLEW': 'slow',
                'PSU_MIO_56_DRIVE_STRENGTH': '4',
                'PSU_MIO_56_SLEW': 'slow',
                'PSU_MIO_57_DRIVE_STRENGTH': '4',
                'PSU_MIO_57_SLEW': 'slow',
                'PSU_MIO_58_DRIVE_STRENGTH': '4',
                'PSU_MIO_58_SLEW': 'slow',
                'PSU_MIO_59_DRIVE_STRENGTH': '4',
                'PSU_MIO_59_SLEW': 'slow',
                'PSU_MIO_5_DRIVE_STRENGTH': '4',
                'PSU_MIO_5_SLEW': 'slow',
                'PSU_MIO_60_DRIVE_STRENGTH': '4',
                'PSU_MIO_60_SLEW': 'slow',
                'PSU_MIO_61_DRIVE_STRENGTH': '4',
                'PSU_MIO_61_SLEW': 'slow',
                'PSU_MIO_62_DRIVE_STRENGTH': '4',
                'PSU_MIO_62_SLEW': 'slow',
                'PSU_MIO_63_DRIVE_STRENGTH': '4',
                'PSU_MIO_63_SLEW': 'slow',
                'PSU_MIO_64_DRIVE_STRENGTH': '4',
                'PSU_MIO_64_SLEW': 'slow',
                'PSU_MIO_65_DRIVE_STRENGTH': '4',
                'PSU_MIO_65_SLEW': 'slow',
                'PSU_MIO_66_DRIVE_STRENGTH': '4',
                'PSU_MIO_66_SLEW': 'slow',
                'PSU_MIO_67_DRIVE_STRENGTH': '4',
                'PSU_MIO_67_SLEW': 'slow',
                'PSU_MIO_68_DRIVE_STRENGTH': '4',
                'PSU_MIO_68_SLEW': 'slow',
                'PSU_MIO_69_DRIVE_STRENGTH': '4',
                'PSU_MIO_69_SLEW': 'slow',
                'PSU_MIO_6_DRIVE_STRENGTH': '4',
                'PSU_MIO_6_SLEW': 'slow',
                'PSU_MIO_71_PULLUPDOWN': 'disable',
                'PSU_MIO_73_PULLUPDOWN': 'disable',
                'PSU_MIO_75_PULLUPDOWN': 'disable',
                'PSU_MIO_76_DRIVE_STRENGTH': '4',
                'PSU_MIO_76_SLEW': 'slow',
                'PSU_MIO_77_DRIVE_STRENGTH': '4',
                'PSU_MIO_77_SLEW': 'slow',
                'PSU_MIO_7_DRIVE_STRENGTH': '4',
                'PSU_MIO_7_SLEW': 'slow',
                'PSU_MIO_8_DRIVE_STRENGTH': '4',
                'PSU_MIO_8_SLEW': 'slow',
                'PSU_MIO_9_DRIVE_STRENGTH': '4',
                'PSU_MIO_9_SLEW': 'slow',
                'PSU__CAN1__PERIPHERAL__ENABLE': '0',
                'PSU__CRF_APB__ACPU_CTRL__FREQMHZ': '1333.333',
                'PSU__CRF_APB__ACPU_CTRL__SRCSEL': 'APLL',
                'PSU__CRF_APB__ACPU__FRAC_ENABLED': '1',
                'PSU__CRF_APB__APLL_CTRL__SRCSEL': 'PSS_REF_CLK',
                'PSU__CRF_APB__DBG_FPD_CTRL__FREQMHZ': '250',
                'PSU__CRF_APB__DBG_FPD_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRF_APB__DBG_TRACE_CTRL__FREQMHZ': '250',
                'PSU__CRF_APB__DBG_TRACE_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRF_APB__DBG_TSTMP_CTRL__FREQMHZ': '250',
                'PSU__CRF_APB__DBG_TSTMP_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRF_APB__DDR_CTRL__FREQMHZ': '1200',
                'PSU__CRF_APB__DDR_CTRL__SRCSEL': 'DPLL',
                'PSU__CRF_APB__DPDMA_REF_CTRL__FREQMHZ': '600',
                'PSU__CRF_APB__DPDMA_REF_CTRL__SRCSEL': 'APLL',
                'PSU__CRF_APB__DPLL_CTRL__SRCSEL': 'PSS_REF_CLK',
                'PSU__CRF_APB__DP_AUDIO_REF_CTRL__SRCSEL': 'RPLL',
                'PSU__CRF_APB__DP_STC_REF_CTRL__SRCSEL': 'RPLL',
                'PSU__CRF_APB__DP_VIDEO_REF_CTRL__SRCSEL': 'VPLL',
                'PSU__CRF_APB__GDMA_REF_CTRL__FREQMHZ': '600',
                'PSU__CRF_APB__GDMA_REF_CTRL__SRCSEL': 'DPLL',
                'PSU__CRF_APB__GPU_REF_CTRL__FREQMHZ': '600',
                'PSU__CRF_APB__GPU_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRF_APB__SATA_REF_CTRL__FREQMHZ': '250',
                'PSU__CRF_APB__SATA_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRF_APB__TOPSW_LSBUS_CTRL__FREQMHZ': '100',
                'PSU__CRF_APB__TOPSW_LSBUS_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRF_APB__TOPSW_MAIN_CTRL__FREQMHZ': '533.33',
                'PSU__CRF_APB__TOPSW_MAIN_CTRL__SRCSEL': 'DPLL',
                'PSU__CRF_APB__VPLL_CTRL__SRCSEL': 'PSS_REF_CLK',
                'PSU__CRL_APB__ADMA_REF_CTRL__FREQMHZ': '500',
                'PSU__CRL_APB__ADMA_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__CPU_R5_CTRL__FREQMHZ': '533.333',
                'PSU__CRL_APB__CPU_R5_CTRL__SRCSEL': 'RPLL',
                'PSU__CRL_APB__DBG_LPD_CTRL__FREQMHZ': '250',
                'PSU__CRL_APB__DBG_LPD_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__GEM3_REF_CTRL__FREQMHZ': '125',
                'PSU__CRL_APB__GEM3_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__I2C1_REF_CTRL__FREQMHZ': '100',
                'PSU__CRL_APB__I2C1_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__IOPLL_CTRL__SRCSEL': 'PSS_REF_CLK',
                'PSU__CRL_APB__IOU_SWITCH_CTRL__FREQMHZ': '250',
                'PSU__CRL_APB__IOU_SWITCH_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__LPD_LSBUS_CTRL__FREQMHZ': '100',
                'PSU__CRL_APB__LPD_LSBUS_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__LPD_SWITCH_CTRL__FREQMHZ': '500',
                'PSU__CRL_APB__LPD_SWITCH_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__PCAP_CTRL__FREQMHZ': '200',
                'PSU__CRL_APB__PCAP_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ': '100',
                'PSU__CRL_APB__PL0_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__PL1_REF_CTRL__FREQMHZ': '100',
                'PSU__CRL_APB__PL1_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__QSPI_REF_CTRL__FREQMHZ': '125',
                'PSU__CRL_APB__QSPI_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__RPLL_CTRL__SRCSEL': 'PSS_REF_CLK',
                'PSU__CRL_APB__SDIO1_REF_CTRL__FREQMHZ': '200',
                'PSU__CRL_APB__SDIO1_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__SPI1_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__TIMESTAMP_REF_CTRL__FREQMHZ': '100',
                'PSU__CRL_APB__TIMESTAMP_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__UART1_REF_CTRL__FREQMHZ': '100',
                'PSU__CRL_APB__UART1_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__USB0_BUS_REF_CTRL__FREQMHZ': '250',
                'PSU__CRL_APB__USB0_BUS_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__CRL_APB__USB3_DUAL_REF_CTRL__FREQMHZ': '20',
                'PSU__CRL_APB__USB3_DUAL_REF_CTRL__SRCSEL': 'IOPLL',
                'PSU__DDRC__BANK_ADDR_COUNT': '2',
                'PSU__DDRC__BG_ADDR_COUNT': '1',
                'PSU__DDRC__BRC_MAPPING': 'ROW_BANK_COL',
                'PSU__DDRC__BUS_WIDTH': '64 Bit',
                'PSU__DDRC__CL': '16',
                'PSU__DDRC__CLOCK_STOP_EN': '0',
                'PSU__DDRC__COL_ADDR_COUNT': '10',
                'PSU__DDRC__COMPONENTS': 'Components',
                'PSU__DDRC__CWL': '14',
                'PSU__DDRC__DDR4_ADDR_MAPPING': '0',
                'PSU__DDRC__DDR4_CAL_MODE_ENABLE': '0',
                'PSU__DDRC__DDR4_CRC_CONTROL': '0',
                'PSU__DDRC__DDR4_T_REF_MODE': '0',
                'PSU__DDRC__DDR4_T_REF_RANGE': 'Normal (0-85)',
                'PSU__DDRC__DEVICE_CAPACITY': '8192 MBits',
                'PSU__DDRC__DIMM_ADDR_MIRROR': '0',
                'PSU__DDRC__DM_DBI': 'DM_NO_DBI',
                'PSU__DDRC__DRAM_WIDTH': '16 Bits',
                'PSU__DDRC__ECC': 'Disabled',
                'PSU__DDRC__FGRM': '1X',
                'PSU__DDRC__LP_ASR': 'manual normal',
                'PSU__DDRC__MEMORY_TYPE': 'DDR 4',
                'PSU__DDRC__PARITY_ENABLE': '0',
                'PSU__DDRC__PER_BANK_REFRESH': '0',
                'PSU__DDRC__PHY_DBI_MODE': '0',
                'PSU__DDRC__RANK_ADDR_COUNT': '0',
                'PSU__DDRC__ROW_ADDR_COUNT': '16',
                'PSU__DDRC__SELF_REF_ABORT': '0',
                'PSU__DDRC__SPEED_BIN': 'DDR4_2400R',
                'PSU__DDRC__STATIC_RD_MODE': '0',
                'PSU__DDRC__TRAIN_DATA_EYE': '1',
                'PSU__DDRC__TRAIN_READ_GATE': '1',
                'PSU__DDRC__TRAIN_WRITE_LEVEL': '1',
                'PSU__DDRC__T_FAW': '30.0',
                'PSU__DDRC__T_RAS_MIN': '33',
                'PSU__DDRC__T_RC': '47.06',
                'PSU__DDRC__T_RCD': '16',
                'PSU__DDRC__T_RP': '16',
                'PSU__DDRC__VREF': '1',
                'PSU__DISPLAYPORT__LANE0__ENABLE': '1',
                'PSU__DISPLAYPORT__LANE0__IO': 'GT Lane1',
                'PSU__DISPLAYPORT__LANE1__ENABLE': '1',
                'PSU__DISPLAYPORT__LANE1__IO': 'GT Lane0',
                'PSU__DISPLAYPORT__PERIPHERAL__ENABLE': '1',
                'PSU__DPAUX__PERIPHERAL__ENABLE': '1',
                'PSU__DPAUX__PERIPHERAL__IO': 'MIO 27 .. 30',
                'PSU__DP__LANE_SEL': 'Dual Lower',
                'PSU__DP__REF_CLK_FREQ': '27',
                'PSU__DP__REF_CLK_SEL': 'Ref Clk0',
                'PSU__ENET3__GRP_MDIO__ENABLE': '1',
                'PSU__ENET3__GRP_MDIO__IO': 'MIO 76 .. 77',
                'PSU__ENET3__PERIPHERAL__ENABLE': '1',
                'PSU__ENET3__PERIPHERAL__IO': 'MIO 64 .. 75',
                'PSU__FPGA_PL0_ENABLE': '1',
                'PSU__FPGA_PL1_ENABLE': '1',
                'PSU__GPIO0_MIO__IO': 'MIO 0 .. 25',
                'PSU__GPIO0_MIO__PERIPHERAL__ENABLE': '1',
                'PSU__GPIO1_MIO__IO': 'MIO 26 .. 51',
                'PSU__GPIO1_MIO__PERIPHERAL__ENABLE': '1',
                'PSU__I2C0__PERIPHERAL__ENABLE': '0',
                'PSU__I2C1__PERIPHERAL__ENABLE': '1',
                'PSU__I2C1__PERIPHERAL__IO': 'MIO 24 .. 25',
                'PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC0_SEL': 'APB',
                'PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC1_SEL': 'APB',
                'PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC2_SEL': 'APB',
                'PSU__IOU_SLCR__IOU_TTC_APB_CLK__TTC3_SEL': 'APB',
                'PSU__OVERRIDE__BASIC_CLOCK': '0',
                'PSU__PMU__GPI0__ENABLE': '1',
                'PSU__PMU__GPI1__ENABLE': '0',
                'PSU__PMU__GPI2__ENABLE': '0',
                'PSU__PMU__GPI3__ENABLE': '0',
                'PSU__PMU__GPI4__ENABLE': '0',
                'PSU__PMU__GPI5__ENABLE': '1',
                'PSU__PMU__GPO0__ENABLE': '1',
                'PSU__PMU__GPO1__ENABLE': '1',
                'PSU__PMU__GPO2__ENABLE': '1',
                'PSU__PMU__GPO2__POLARITY': 'high',
                'PSU__PMU__GPO3__ENABLE': '1',
                'PSU__PMU__GPO4__ENABLE': '0',
                'PSU__PMU__GPO5__ENABLE': '0',
                'PSU__PMU__PERIPHERAL__ENABLE': '1',
                'PSU__PRESET_APPLIED': '1',
                'PSU__PSS_REF_CLK__FREQMHZ': '33.333',
                'PSU__QSPI__GRP_FBCLK__ENABLE': '0',
                'PSU__QSPI__PERIPHERAL__DATA_MODE': 'x4',
                'PSU__QSPI__PERIPHERAL__ENABLE': '1',
                'PSU__QSPI__PERIPHERAL__IO': 'MIO 0 .. 5',
                'PSU__QSPI__PERIPHERAL__MODE': 'Single',
                'PSU__SATA__REF_CLK_FREQ': '125',
                'PSU__SATA__REF_CLK_SEL': 'Ref Clk2',
                'PSU__SD1__DATA_TRANSFER_MODE': '8Bit',
                'PSU__SD1__GRP_CD__ENABLE': '1',
                'PSU__SD1__GRP_CD__IO': 'MIO 45',
                'PSU__SD1__GRP_POW__ENABLE': '1',
                'PSU__SD1__GRP_POW__IO': 'MIO 43',
                'PSU__SD1__PERIPHERAL__ENABLE': '1',
                'PSU__SD1__PERIPHERAL__IO': 'MIO 39 .. 51',
                'PSU__SD1__SLOT_TYPE': 'SD 3.0',
                'PSU__SPI1__GRP_SS1__ENABLE': '0',
                'PSU__SPI1__PERIPHERAL__ENABLE': '1',
                'PSU__SWDT0__PERIPHERAL__ENABLE': '1',
                'PSU__SWDT1__PERIPHERAL__ENABLE': '1',
                'PSU__TTC0__PERIPHERAL__ENABLE': '1',
                'PSU__TTC1__PERIPHERAL__ENABLE': '1',
                'PSU__TTC2__PERIPHERAL__ENABLE': '1',
                'PSU__TTC3__PERIPHERAL__ENABLE': '1',
                'PSU__UART1__PERIPHERAL__ENABLE': '1',
                'PSU__UART1__PERIPHERAL__IO': 'MIO 36 .. 37',
                'PSU__USB0__PERIPHERAL__ENABLE': '1',
                'PSU__USB0__PERIPHERAL__IO': 'MIO 52 .. 63',
                'PSU__USB0__REF_CLK_FREQ': '26',
                'PSU__USB0__REF_CLK_SEL': 'Ref Clk1',
                'PSU__USB0__RESET__ENABLE': '1',
                'PSU__USB3_0__PERIPHERAL__ENABLE': '1',
                'PSU__USB3_0__PERIPHERAL__IO': 'GT Lane2',
                'PSU__USB__RESET__MODE': 'Boot Pin',
                'PSU__USE__IRQ0': '1'})
            # Connect Zynq AXI master to the SoC
            wb_gp0 = wishbone.Interface()
            self.submodules += axi.AXI2Wishbone(
                axi          = self.cpu.add_axi_gp_master(),
                wishbone     = wb_gp0,
                base_address = self.mem_map["csr"])
            self.add_wb_master(wb_gp0)
            self.bus.add_region("sram", SoCRegion(
                origin=self.cpu.mem_map["sram"],
                size=2 * 1024 * 1024 * 1024)  # DDR
            )
            self.bus.add_region("rom", SoCRegion(
                origin=self.cpu.mem_map["rom"],
                size=512 * 1024 * 1024 // 8,
                linker=True)
            )
        #     self.constants['CONFIG_CLOCK_FREQUENCY'] = 666666687
        #
            use_ps7_clk = True
        else:
            use_ps7_clk = False

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

    def finalize(self, *args, **kwargs):
        super(BaseSoC, self).finalize(*args, **kwargs)
        if self.cpu_type != "zynqmp":
            return

        libxil_path = os.path.join(self.builder.software_dir, 'libxil')
        os.makedirs(os.path.realpath(libxil_path), exist_ok=True)
        lib = os.path.join(libxil_path, 'embeddedsw')
        if not os.path.exists(lib):
            os.system("git clone --depth 1 https://github.com/Xilinx/embeddedsw {}".format(lib))

        os.makedirs(os.path.realpath(self.builder.include_dir), exist_ok=True)

        for header in [
            'XilinxProcessorIPLib/drivers/uartps/src/xuartps_hw.h',
            'lib/bsp/standalone/src/common/xil_types.h',
            'lib/bsp/standalone/src/common/xil_assert.h',
            'lib/bsp/standalone/src/common/xil_io.h',
            'lib/bsp/standalone/src/common/xil_printf.h',
            'lib/bsp/standalone/src/common/xstatus.h',
            'lib/bsp/standalone/src/common/xdebug.h',
            'lib/bsp/standalone/src/arm/cortexa9/xpseudo_asm.h',
            'lib/bsp/standalone/src/arm/cortexa9/xreg_cortexa9.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_cache.h',
            'lib/bsp/standalone/src/arm/cortexa9/xparameters_ps.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_errata.h',
            'lib/bsp/standalone/src/arm/cortexa9/xtime_l.h',
            'lib/bsp/standalone/src/arm/common/xil_exception.h',
            'lib/bsp/standalone/src/arm/common/gcc/xpseudo_asm_gcc.h',
        ]:
            shutil.copy(os.path.join(lib, header), self.builder.include_dir)
        write_to_file(os.path.join(self.builder.include_dir, 'bspconfig.h'), """
#ifndef BSPCONFIG_H  /* prevent circular inclusions */
#define BSPCONFIG_H  /* by using protection macros */

#define MICROBLAZE_PVR_NONE
#define EL3 1
#define EL1_NONSECURE 0
#define HYP_GUEST 0

#endif /*end of __BSPCONFIG_H_*/
""")
        write_to_file(os.path.join(self.builder.include_dir, 'xparameters.h'), '''
#ifndef XPARAMETERS_H   /* prevent circular inclusions */
#define XPARAMETERS_H   /* by using protection macros */

/* Definition for CPU ID */
#define XPAR_CPU_ID 0U

/* Definitions for peripheral PSU_CORTEXA53_0 */
#define XPAR_PSU_CORTEXA53_0_CPU_CLK_FREQ_HZ 1333333008
#define XPAR_PSU_CORTEXA53_0_TIMESTAMP_CLK_FREQ 99999001


/******************************************************************/

/* Canonical definitions for peripheral PSU_CORTEXA53_0 */
#define XPAR_CPU_CORTEXA53_0_CPU_CLK_FREQ_HZ 1333333008
#define XPAR_CPU_CORTEXA53_0_TIMESTAMP_CLK_FREQ 99999001


/******************************************************************/


/* Definitions for interface M_AXI_HPM0_FPD_0 */
#define XPAR_M_AXI_HPM0_FPD_0_BASEADDR 0xA0000000
#define XPAR_M_AXI_HPM0_FPD_0_HIGHADDR 0xA000FFFF

 /* Definition for PSS REF CLK FREQUENCY */
#define XPAR_PSU_PSS_REF_CLK_FREQ_HZ 33333000U

#include "xparameters_ps.h"

#define XPS_BOARD_KV260_SOM


/* Number of Fabric Resets */
#define XPAR_NUM_FABRIC_RESETS 1

#define STDIN_BASEADDRESS 0xFF010000
#define STDOUT_BASEADDRESS 0xFF010000

/******************************************************************/

/* Platform specific definitions */
#define PLATFORM_ZYNQMP
 
/* Definitions for sleep timer configuration */
#define XSLEEP_TIMER_IS_DEFAULT_TIMER
 
 
/******************************************************************/
/* Definitions for driver AXIPMON */
#define XPAR_XAXIPMON_NUM_INSTANCES 4U

/* Definitions for peripheral PSU_APM_0 */
#define XPAR_PSU_APM_0_DEVICE_ID 0U
#define XPAR_PSU_APM_0_BASEADDR 0xFD0B0000U
#define XPAR_PSU_APM_0_HIGHADDR 0xFD0BFFFFU
#define XPAR_PSU_APM_0_GLOBAL_COUNT_WIDTH 32U
#define XPAR_PSU_APM_0_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_PSU_APM_0_ENABLE_EVENT_COUNT 1U
#define XPAR_PSU_APM_0_NUM_MONITOR_SLOTS 6U
#define XPAR_PSU_APM_0_NUM_OF_COUNTERS 10U
#define XPAR_PSU_APM_0_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_PSU_APM_0_ENABLE_EVENT_LOG 0U
#define XPAR_PSU_APM_0_FIFO_AXIS_DEPTH 32U
#define XPAR_PSU_APM_0_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_PSU_APM_0_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_PSU_APM_0_METRIC_COUNT_SCALE 1U
#define XPAR_PSU_APM_0_ENABLE_ADVANCED 1U
#define XPAR_PSU_APM_0_ENABLE_PROFILE 0U
#define XPAR_PSU_APM_0_ENABLE_TRACE 0U
#define XPAR_PSU_APM_0_S_AXI4_BASEADDR 0x00000000U
#define XPAR_PSU_APM_0_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_PSU_APM_0_ENABLE_32BIT_FILTER_ID 1U


/* Definitions for peripheral PSU_APM_1 */
#define XPAR_PSU_APM_1_DEVICE_ID 1U
#define XPAR_PSU_APM_1_BASEADDR 0xFFA00000U
#define XPAR_PSU_APM_1_HIGHADDR 0xFFA0FFFFU
#define XPAR_PSU_APM_1_GLOBAL_COUNT_WIDTH 32U
#define XPAR_PSU_APM_1_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_PSU_APM_1_ENABLE_EVENT_COUNT 1U
#define XPAR_PSU_APM_1_NUM_MONITOR_SLOTS 1U
#define XPAR_PSU_APM_1_NUM_OF_COUNTERS 3U
#define XPAR_PSU_APM_1_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_PSU_APM_1_ENABLE_EVENT_LOG 0U
#define XPAR_PSU_APM_1_FIFO_AXIS_DEPTH 32U
#define XPAR_PSU_APM_1_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_PSU_APM_1_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_PSU_APM_1_METRIC_COUNT_SCALE 1U
#define XPAR_PSU_APM_1_ENABLE_ADVANCED 1U
#define XPAR_PSU_APM_1_ENABLE_PROFILE 0U
#define XPAR_PSU_APM_1_ENABLE_TRACE 0U
#define XPAR_PSU_APM_1_S_AXI4_BASEADDR 0x00000000U
#define XPAR_PSU_APM_1_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_PSU_APM_1_ENABLE_32BIT_FILTER_ID 1U


/* Definitions for peripheral PSU_APM_2 */
#define XPAR_PSU_APM_2_DEVICE_ID 2U
#define XPAR_PSU_APM_2_BASEADDR 0xFFA10000U
#define XPAR_PSU_APM_2_HIGHADDR 0xFFA1FFFFU
#define XPAR_PSU_APM_2_GLOBAL_COUNT_WIDTH 32U
#define XPAR_PSU_APM_2_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_PSU_APM_2_ENABLE_EVENT_COUNT 1U
#define XPAR_PSU_APM_2_NUM_MONITOR_SLOTS 1U
#define XPAR_PSU_APM_2_NUM_OF_COUNTERS 3U
#define XPAR_PSU_APM_2_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_PSU_APM_2_ENABLE_EVENT_LOG 0U
#define XPAR_PSU_APM_2_FIFO_AXIS_DEPTH 32U
#define XPAR_PSU_APM_2_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_PSU_APM_2_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_PSU_APM_2_METRIC_COUNT_SCALE 1U
#define XPAR_PSU_APM_2_ENABLE_ADVANCED 1U
#define XPAR_PSU_APM_2_ENABLE_PROFILE 0U
#define XPAR_PSU_APM_2_ENABLE_TRACE 0U
#define XPAR_PSU_APM_2_S_AXI4_BASEADDR 0x00000000U
#define XPAR_PSU_APM_2_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_PSU_APM_2_ENABLE_32BIT_FILTER_ID 1U


/* Definitions for peripheral PSU_APM_5 */
#define XPAR_PSU_APM_5_DEVICE_ID 3U
#define XPAR_PSU_APM_5_BASEADDR 0xFD490000U
#define XPAR_PSU_APM_5_HIGHADDR 0xFD49FFFFU
#define XPAR_PSU_APM_5_GLOBAL_COUNT_WIDTH 32U
#define XPAR_PSU_APM_5_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_PSU_APM_5_ENABLE_EVENT_COUNT 1U
#define XPAR_PSU_APM_5_NUM_MONITOR_SLOTS 1U
#define XPAR_PSU_APM_5_NUM_OF_COUNTERS 3U
#define XPAR_PSU_APM_5_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_PSU_APM_5_ENABLE_EVENT_LOG 0U
#define XPAR_PSU_APM_5_FIFO_AXIS_DEPTH 32U
#define XPAR_PSU_APM_5_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_PSU_APM_5_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_PSU_APM_5_METRIC_COUNT_SCALE 1U
#define XPAR_PSU_APM_5_ENABLE_ADVANCED 1U
#define XPAR_PSU_APM_5_ENABLE_PROFILE 0U
#define XPAR_PSU_APM_5_ENABLE_TRACE 0U
#define XPAR_PSU_APM_5_S_AXI4_BASEADDR 0x00000000U
#define XPAR_PSU_APM_5_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_PSU_APM_5_ENABLE_32BIT_FILTER_ID 1U


/******************************************************************/

/* Canonical definitions for peripheral PSU_APM_0 */
#define XPAR_AXIPMON_0_DEVICE_ID XPAR_PSU_APM_0_DEVICE_ID
#define XPAR_AXIPMON_0_BASEADDR 0xFD0B0000U
#define XPAR_AXIPMON_0_HIGHADDR 0xFD0BFFFFU
#define XPAR_AXIPMON_0_GLOBAL_COUNT_WIDTH 32U
#define XPAR_AXIPMON_0_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_AXIPMON_0_ENABLE_EVENT_COUNT 1U
#define XPAR_AXIPMON_0_NUM_MONITOR_SLOTS 6U
#define XPAR_AXIPMON_0_NUM_OF_COUNTERS 10U
#define XPAR_AXIPMON_0_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_AXIPMON_0_ENABLE_EVENT_LOG 0U
#define XPAR_AXIPMON_0_FIFO_AXIS_DEPTH 32U
#define XPAR_AXIPMON_0_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_AXIPMON_0_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_AXIPMON_0_METRIC_COUNT_SCALE 1U
#define XPAR_AXIPMON_0_ENABLE_ADVANCED 1U
#define XPAR_AXIPMON_0_ENABLE_PROFILE 0U
#define XPAR_AXIPMON_0_ENABLE_TRACE 0U
#define XPAR_AXIPMON_0_S_AXI4_BASEADDR 0x00000000U
#define XPAR_AXIPMON_0_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_AXIPMON_0_ENABLE_32BIT_FILTER_ID 1U

/* Canonical definitions for peripheral PSU_APM_1 */
#define XPAR_AXIPMON_1_DEVICE_ID XPAR_PSU_APM_1_DEVICE_ID
#define XPAR_AXIPMON_1_BASEADDR 0xFFA00000U
#define XPAR_AXIPMON_1_HIGHADDR 0xFFA0FFFFU
#define XPAR_AXIPMON_1_GLOBAL_COUNT_WIDTH 32U
#define XPAR_AXIPMON_1_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_AXIPMON_1_ENABLE_EVENT_COUNT 1U
#define XPAR_AXIPMON_1_NUM_MONITOR_SLOTS 1U
#define XPAR_AXIPMON_1_NUM_OF_COUNTERS 3U
#define XPAR_AXIPMON_1_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_AXIPMON_1_ENABLE_EVENT_LOG 0U
#define XPAR_AXIPMON_1_FIFO_AXIS_DEPTH 32U
#define XPAR_AXIPMON_1_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_AXIPMON_1_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_AXIPMON_1_METRIC_COUNT_SCALE 1U
#define XPAR_AXIPMON_1_ENABLE_ADVANCED 1U
#define XPAR_AXIPMON_1_ENABLE_PROFILE 0U
#define XPAR_AXIPMON_1_ENABLE_TRACE 0U
#define XPAR_AXIPMON_1_S_AXI4_BASEADDR 0x00000000U
#define XPAR_AXIPMON_1_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_AXIPMON_1_ENABLE_32BIT_FILTER_ID 1U

/* Canonical definitions for peripheral PSU_APM_2 */
#define XPAR_AXIPMON_2_DEVICE_ID XPAR_PSU_APM_2_DEVICE_ID
#define XPAR_AXIPMON_2_BASEADDR 0xFFA10000U
#define XPAR_AXIPMON_2_HIGHADDR 0xFFA1FFFFU
#define XPAR_AXIPMON_2_GLOBAL_COUNT_WIDTH 32U
#define XPAR_AXIPMON_2_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_AXIPMON_2_ENABLE_EVENT_COUNT 1U
#define XPAR_AXIPMON_2_NUM_MONITOR_SLOTS 1U
#define XPAR_AXIPMON_2_NUM_OF_COUNTERS 3U
#define XPAR_AXIPMON_2_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_AXIPMON_2_ENABLE_EVENT_LOG 0U
#define XPAR_AXIPMON_2_FIFO_AXIS_DEPTH 32U
#define XPAR_AXIPMON_2_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_AXIPMON_2_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_AXIPMON_2_METRIC_COUNT_SCALE 1U
#define XPAR_AXIPMON_2_ENABLE_ADVANCED 1U
#define XPAR_AXIPMON_2_ENABLE_PROFILE 0U
#define XPAR_AXIPMON_2_ENABLE_TRACE 0U
#define XPAR_AXIPMON_2_S_AXI4_BASEADDR 0x00000000U
#define XPAR_AXIPMON_2_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_AXIPMON_2_ENABLE_32BIT_FILTER_ID 1U

/* Canonical definitions for peripheral PSU_APM_5 */
#define XPAR_AXIPMON_3_DEVICE_ID XPAR_PSU_APM_5_DEVICE_ID
#define XPAR_AXIPMON_3_BASEADDR 0xFD490000U
#define XPAR_AXIPMON_3_HIGHADDR 0xFD49FFFFU
#define XPAR_AXIPMON_3_GLOBAL_COUNT_WIDTH 32U
#define XPAR_AXIPMON_3_METRICS_SAMPLE_COUNT_WIDTH 32U
#define XPAR_AXIPMON_3_ENABLE_EVENT_COUNT 1U
#define XPAR_AXIPMON_3_NUM_MONITOR_SLOTS 1U
#define XPAR_AXIPMON_3_NUM_OF_COUNTERS 3U
#define XPAR_AXIPMON_3_HAVE_SAMPLED_METRIC_CNT 1U
#define XPAR_AXIPMON_3_ENABLE_EVENT_LOG 0U
#define XPAR_AXIPMON_3_FIFO_AXIS_DEPTH 32U
#define XPAR_AXIPMON_3_FIFO_AXIS_TDATA_WIDTH 56U
#define XPAR_AXIPMON_3_FIFO_AXIS_TID_WIDTH 1U
#define XPAR_AXIPMON_3_METRIC_COUNT_SCALE 1U
#define XPAR_AXIPMON_3_ENABLE_ADVANCED 1U
#define XPAR_AXIPMON_3_ENABLE_PROFILE 0U
#define XPAR_AXIPMON_3_ENABLE_TRACE 0U
#define XPAR_AXIPMON_3_S_AXI4_BASEADDR 0x00000000U
#define XPAR_AXIPMON_3_S_AXI4_HIGHADDR 0x00000000U
#define XPAR_AXIPMON_3_ENABLE_32BIT_FILTER_ID 1U


/******************************************************************/

/* Definitions for driver CSUDMA */
#define XPAR_XCSUDMA_NUM_INSTANCES 1

/* Definitions for peripheral PSU_CSUDMA */
#define XPAR_PSU_CSUDMA_DEVICE_ID 0
#define XPAR_PSU_CSUDMA_BASEADDR 0xFFC80000
#define XPAR_PSU_CSUDMA_HIGHADDR 0xFFC9FFFF
#define XPAR_PSU_CSUDMA_CSUDMA_CLK_FREQ_HZ 0


/******************************************************************/

#define XPAR_PSU_CSUDMA_DMATYPE 0
/* Canonical definitions for peripheral PSU_CSUDMA */
#define XPAR_XCSUDMA_0_DEVICE_ID XPAR_PSU_CSUDMA_DEVICE_ID
#define XPAR_XCSUDMA_0_BASEADDR 0xFFC80000
#define XPAR_XCSUDMA_0_HIGHADDR 0xFFC9FFFF
#define XPAR_XCSUDMA_0_CSUDMA_CLK_FREQ_HZ 0


/******************************************************************/

/* Definitions for driver DDRCPSU */
#define XPAR_XDDRCPSU_NUM_INSTANCES 1

/* Definitions for peripheral PSU_DDRC_0 */
#define XPAR_PSU_DDRC_0_DEVICE_ID 0
#define XPAR_PSU_DDRC_0_BASEADDR 0xFD070000
#define XPAR_PSU_DDRC_0_HIGHADDR 0xFD070FFF
#define XPAR_PSU_DDRC_0_HAS_ECC 0
#define XPAR_PSU_DDRC_0_DDRC_CLK_FREQ_HZ 533328002


/******************************************************************/

#define XPAR_PSU_DDRC_0_DDR4_ADDR_MAPPING 0
#define XPAR_PSU_DDRC_0_DDR_FREQ_MHZ 1066.656006
#define XPAR_PSU_DDRC_0_VIDEO_BUFFER_SIZE 0
#define XPAR_PSU_DDRC_0_BRC_MAPPING 0
#define XPAR_PSU_DDRC_0_DDR_MEMORY_TYPE 4
#define XPAR_PSU_DDRC_0_DDR_MEMORY_ADDRESS_MAP 0
#define XPAR_PSU_DDRC_0_DDR_DATA_MASK_AND_DBI 7
#define XPAR_PSU_DDRC_0_DDR_ADDRESS_MIRRORING 0
#define XPAR_PSU_DDRC_0_DDR_2ND_CLOCK 0
#define XPAR_PSU_DDRC_0_DDR_PARITY 0
#define XPAR_PSU_DDRC_0_DDR_POWER_DOWN_ENABLE 0
#define XPAR_PSU_DDRC_0_CLOCK_STOP 0
#define XPAR_PSU_DDRC_0_DDR_LOW_POWER_AUTO_SELF_REFRESH 0
#define XPAR_PSU_DDRC_0_DDR_TEMP_CONTROLLED_REFRESH 0
#define XPAR_PSU_DDRC_0_DDR_MAX_OPERATING_TEMPARATURE 0
#define XPAR_PSU_DDRC_0_DDR_FINE_GRANULARITY_REFRESH_MODE 0
#define XPAR_PSU_DDRC_0_DDR_SELF_REFRESH_ABORT 0
/* Canonical definitions for peripheral PSU_DDRC_0 */
#define XPAR_DDRCPSU_0_DEVICE_ID XPAR_PSU_DDRC_0_DEVICE_ID
#define XPAR_DDRCPSU_0_BASEADDR 0xFD070000
#define XPAR_DDRCPSU_0_HIGHADDR 0xFD070FFF
#define XPAR_DDRCPSU_0_DDRC_CLK_FREQ_HZ 533328002


/******************************************************************/

#define XPAR_DDRCPSU_0_DDR4_ADDR_MAPPING 0
#define XPAR_DDRCPSU_0_DDR_FREQ_MHZ 1066.656006
#define XPAR_DDRCPSU_0_VIDEO_BUFFER_SIZE 0
#define XPAR_DDRCPSU_0_BRC_MAPPING 0
#define XPAR_DDRCPSU_0_DDR_MEMORY_TYPE 4
#define XPAR_DDRCPSU_0_DDR_MEMORY_ADDRESS_MAP 0
#define XPAR_DDRCPSU_0_DDR_DATA_MASK_AND_DBI 7
#define XPAR_DDRCPSU_0_DDR_ADDRESS_MIRRORING 0
#define XPAR_DDRCPSU_0_DDR_2ND_CLOCK 0
#define XPAR_DDRCPSU_0_DDR_PARITY 0
#define XPAR_DDRCPSU_0_DDR_POWER_DOWN_ENABLE 0
#define XPAR_DDRCPSU_0_CLOCK_STOP 0
#define XPAR_DDRCPSU_0_DDR_LOW_POWER_AUTO_SELF_REFRESH 0
#define XPAR_DDRCPSU_0_DDR_TEMP_CONTROLLED_REFRESH 0
#define XPAR_DDRCPSU_0_DDR_MAX_OPERATING_TEMPARATURE 0
#define XPAR_DDRCPSU_0_DDR_FINE_GRANULARITY_REFRESH_MODE 0
#define XPAR_DDRCPSU_0_DDR_SELF_REFRESH_ABORT 0

/* Peripheral Definitions for peripheral PSU_AFI_0 */
#define XPAR_PSU_AFI_0_S_AXI_BASEADDR 0xFD360000
#define XPAR_PSU_AFI_0_S_AXI_HIGHADDR 0xFD36FFFF


/* Peripheral Definitions for peripheral PSU_AFI_1 */
#define XPAR_PSU_AFI_1_S_AXI_BASEADDR 0xFD370000
#define XPAR_PSU_AFI_1_S_AXI_HIGHADDR 0xFD37FFFF


/* Peripheral Definitions for peripheral PSU_AFI_2 */
#define XPAR_PSU_AFI_2_S_AXI_BASEADDR 0xFD380000
#define XPAR_PSU_AFI_2_S_AXI_HIGHADDR 0xFD38FFFF


/* Peripheral Definitions for peripheral PSU_AFI_3 */
#define XPAR_PSU_AFI_3_S_AXI_BASEADDR 0xFD390000
#define XPAR_PSU_AFI_3_S_AXI_HIGHADDR 0xFD39FFFF


/* Peripheral Definitions for peripheral PSU_AFI_4 */
#define XPAR_PSU_AFI_4_S_AXI_BASEADDR 0xFD3A0000
#define XPAR_PSU_AFI_4_S_AXI_HIGHADDR 0xFD3AFFFF


/* Peripheral Definitions for peripheral PSU_AFI_5 */
#define XPAR_PSU_AFI_5_S_AXI_BASEADDR 0xFD3B0000
#define XPAR_PSU_AFI_5_S_AXI_HIGHADDR 0xFD3BFFFF


/* Peripheral Definitions for peripheral PSU_AFI_6 */
#define XPAR_PSU_AFI_6_S_AXI_BASEADDR 0xFF9B0000
#define XPAR_PSU_AFI_6_S_AXI_HIGHADDR 0xFF9BFFFF


/* Peripheral Definitions for peripheral PSU_APU */
#define XPAR_PSU_APU_S_AXI_BASEADDR 0xFD5C0000
#define XPAR_PSU_APU_S_AXI_HIGHADDR 0xFD5CFFFF


/* Peripheral Definitions for peripheral PSU_CCI_GPV */
#define XPAR_PSU_CCI_GPV_S_AXI_BASEADDR 0xFD6E0000
#define XPAR_PSU_CCI_GPV_S_AXI_HIGHADDR 0xFD6EFFFF


/* Peripheral Definitions for peripheral PSU_CCI_REG */
#define XPAR_PSU_CCI_REG_S_AXI_BASEADDR 0xFD5E0000
#define XPAR_PSU_CCI_REG_S_AXI_HIGHADDR 0xFD5EFFFF


/* Peripheral Definitions for peripheral PSU_CRL_APB */
#define XPAR_PSU_CRL_APB_S_AXI_BASEADDR 0xFF5E0000
#define XPAR_PSU_CRL_APB_S_AXI_HIGHADDR 0xFF85FFFF


/* Peripheral Definitions for peripheral PSU_CSU_0 */
#define XPAR_PSU_CSU_0_S_AXI_BASEADDR 0xFFCA0000
#define XPAR_PSU_CSU_0_S_AXI_HIGHADDR 0xFFCAFFFF


/* Peripheral Definitions for peripheral PSU_CTRL_IPI */
#define XPAR_PSU_CTRL_IPI_S_AXI_BASEADDR 0xFF380000
#define XPAR_PSU_CTRL_IPI_S_AXI_HIGHADDR 0xFF3FFFFF


/* Peripheral Definitions for peripheral PSU_DDR_0 */
#define XPAR_PSU_DDR_0_S_AXI_BASEADDR 0x00000000
#define XPAR_PSU_DDR_0_S_AXI_HIGHADDR 0x7FFFFFFF


/* Peripheral Definitions for peripheral PSU_DDR_1 */
#define XPAR_PSU_DDR_1_S_AXI_BASEADDR 0x800000000
#define XPAR_PSU_DDR_1_S_AXI_HIGHADDR 0x87FFFFFFF


/* Peripheral Definitions for peripheral PSU_DDR_PHY */
#define XPAR_PSU_DDR_PHY_S_AXI_BASEADDR 0xFD080000
#define XPAR_PSU_DDR_PHY_S_AXI_HIGHADDR 0xFD08FFFF


/* Peripheral Definitions for peripheral PSU_DDR_QOS_CTRL */
#define XPAR_PSU_DDR_QOS_CTRL_S_AXI_BASEADDR 0xFD090000
#define XPAR_PSU_DDR_QOS_CTRL_S_AXI_HIGHADDR 0xFD09FFFF


/* Peripheral Definitions for peripheral PSU_DDR_XMPU0_CFG */
#define XPAR_PSU_DDR_XMPU0_CFG_S_AXI_BASEADDR 0xFD000000
#define XPAR_PSU_DDR_XMPU0_CFG_S_AXI_HIGHADDR 0xFD00FFFF


/* Peripheral Definitions for peripheral PSU_DDR_XMPU1_CFG */
#define XPAR_PSU_DDR_XMPU1_CFG_S_AXI_BASEADDR 0xFD010000
#define XPAR_PSU_DDR_XMPU1_CFG_S_AXI_HIGHADDR 0xFD01FFFF


/* Peripheral Definitions for peripheral PSU_DDR_XMPU2_CFG */
#define XPAR_PSU_DDR_XMPU2_CFG_S_AXI_BASEADDR 0xFD020000
#define XPAR_PSU_DDR_XMPU2_CFG_S_AXI_HIGHADDR 0xFD02FFFF


/* Peripheral Definitions for peripheral PSU_DDR_XMPU3_CFG */
#define XPAR_PSU_DDR_XMPU3_CFG_S_AXI_BASEADDR 0xFD030000
#define XPAR_PSU_DDR_XMPU3_CFG_S_AXI_HIGHADDR 0xFD03FFFF


/* Peripheral Definitions for peripheral PSU_DDR_XMPU4_CFG */
#define XPAR_PSU_DDR_XMPU4_CFG_S_AXI_BASEADDR 0xFD040000
#define XPAR_PSU_DDR_XMPU4_CFG_S_AXI_HIGHADDR 0xFD04FFFF


/* Peripheral Definitions for peripheral PSU_DDR_XMPU5_CFG */
#define XPAR_PSU_DDR_XMPU5_CFG_S_AXI_BASEADDR 0xFD050000
#define XPAR_PSU_DDR_XMPU5_CFG_S_AXI_HIGHADDR 0xFD05FFFF


/* Peripheral Definitions for peripheral PSU_EFUSE */
#define XPAR_PSU_EFUSE_S_AXI_BASEADDR 0xFFCC0000
#define XPAR_PSU_EFUSE_S_AXI_HIGHADDR 0xFFCCFFFF


/* Peripheral Definitions for peripheral PSU_FPD_GPV */
#define XPAR_PSU_FPD_GPV_S_AXI_BASEADDR 0xFD700000
#define XPAR_PSU_FPD_GPV_S_AXI_HIGHADDR 0xFD7FFFFF


/* Peripheral Definitions for peripheral PSU_FPD_SLCR */
#define XPAR_PSU_FPD_SLCR_S_AXI_BASEADDR 0xFD610000
#define XPAR_PSU_FPD_SLCR_S_AXI_HIGHADDR 0xFD68FFFF


/* Peripheral Definitions for peripheral PSU_FPD_SLCR_SECURE */
#define XPAR_PSU_FPD_SLCR_SECURE_S_AXI_BASEADDR 0xFD690000
#define XPAR_PSU_FPD_SLCR_SECURE_S_AXI_HIGHADDR 0xFD6CFFFF


/* Peripheral Definitions for peripheral PSU_FPD_XMPU_CFG */
#define XPAR_PSU_FPD_XMPU_CFG_S_AXI_BASEADDR 0xFD5D0000
#define XPAR_PSU_FPD_XMPU_CFG_S_AXI_HIGHADDR 0xFD5DFFFF


/* Peripheral Definitions for peripheral PSU_FPD_XMPU_SINK */
#define XPAR_PSU_FPD_XMPU_SINK_S_AXI_BASEADDR 0xFD4F0000
#define XPAR_PSU_FPD_XMPU_SINK_S_AXI_HIGHADDR 0xFD4FFFFF


/* Peripheral Definitions for peripheral PSU_GPU */
#define XPAR_PSU_GPU_S_AXI_BASEADDR 0xFD4B0000
#define XPAR_PSU_GPU_S_AXI_HIGHADDR 0xFD4BFFFF


/* Peripheral Definitions for peripheral PSU_IOU_SCNTR */
#define XPAR_PSU_IOU_SCNTR_S_AXI_BASEADDR 0xFF250000
#define XPAR_PSU_IOU_SCNTR_S_AXI_HIGHADDR 0xFF25FFFF


/* Peripheral Definitions for peripheral PSU_IOU_SCNTRS */
#define XPAR_PSU_IOU_SCNTRS_S_AXI_BASEADDR 0xFF260000
#define XPAR_PSU_IOU_SCNTRS_S_AXI_HIGHADDR 0xFF26FFFF


/* Peripheral Definitions for peripheral PSU_IOUSECURE_SLCR */
#define XPAR_PSU_IOUSECURE_SLCR_S_AXI_BASEADDR 0xFF240000
#define XPAR_PSU_IOUSECURE_SLCR_S_AXI_HIGHADDR 0xFF24FFFF


/* Peripheral Definitions for peripheral PSU_IOUSLCR_0 */
#define XPAR_PSU_IOUSLCR_0_S_AXI_BASEADDR 0xFF180000
#define XPAR_PSU_IOUSLCR_0_S_AXI_HIGHADDR 0xFF23FFFF


/* Peripheral Definitions for peripheral PSU_LPD_SLCR */
#define XPAR_PSU_LPD_SLCR_S_AXI_BASEADDR 0xFF410000
#define XPAR_PSU_LPD_SLCR_S_AXI_HIGHADDR 0xFF4AFFFF


/* Peripheral Definitions for peripheral PSU_LPD_SLCR_SECURE */
#define XPAR_PSU_LPD_SLCR_SECURE_S_AXI_BASEADDR 0xFF4B0000
#define XPAR_PSU_LPD_SLCR_SECURE_S_AXI_HIGHADDR 0xFF4DFFFF


/* Peripheral Definitions for peripheral PSU_LPD_XPPU */
#define XPAR_PSU_LPD_XPPU_S_AXI_BASEADDR 0xFF980000
#define XPAR_PSU_LPD_XPPU_S_AXI_HIGHADDR 0xFF99FFFF


/* Peripheral Definitions for peripheral PSU_LPD_XPPU_SINK */
#define XPAR_PSU_LPD_XPPU_SINK_S_AXI_BASEADDR 0xFF9C0000
#define XPAR_PSU_LPD_XPPU_SINK_S_AXI_HIGHADDR 0xFF9CFFFF


/* Peripheral Definitions for peripheral PSU_MBISTJTAG */
#define XPAR_PSU_MBISTJTAG_S_AXI_BASEADDR 0xFFCF0000
#define XPAR_PSU_MBISTJTAG_S_AXI_HIGHADDR 0xFFCFFFFF


/* Peripheral Definitions for peripheral PSU_MESSAGE_BUFFERS */
#define XPAR_PSU_MESSAGE_BUFFERS_S_AXI_BASEADDR 0xFF990000
#define XPAR_PSU_MESSAGE_BUFFERS_S_AXI_HIGHADDR 0xFF99FFFF


/* Peripheral Definitions for peripheral PSU_OCM */
#define XPAR_PSU_OCM_S_AXI_BASEADDR 0xFF960000
#define XPAR_PSU_OCM_S_AXI_HIGHADDR 0xFF96FFFF


/* Peripheral Definitions for peripheral PSU_OCM_RAM_0 */
#define XPAR_PSU_OCM_RAM_0_S_AXI_BASEADDR 0xFFFC0000
#define XPAR_PSU_OCM_RAM_0_S_AXI_HIGHADDR 0xFFFFFFFF


/* Peripheral Definitions for peripheral PSU_OCM_XMPU_CFG */
#define XPAR_PSU_OCM_XMPU_CFG_S_AXI_BASEADDR 0xFFA70000
#define XPAR_PSU_OCM_XMPU_CFG_S_AXI_HIGHADDR 0xFFA7FFFF


/* Peripheral Definitions for peripheral PSU_PMU_GLOBAL_0 */
#define XPAR_PSU_PMU_GLOBAL_0_S_AXI_BASEADDR 0xFFD80000
#define XPAR_PSU_PMU_GLOBAL_0_S_AXI_HIGHADDR 0xFFDBFFFF


/* Peripheral Definitions for peripheral PSU_QSPI_LINEAR_0 */
#define XPAR_PSU_QSPI_LINEAR_0_S_AXI_BASEADDR 0xC0000000
#define XPAR_PSU_QSPI_LINEAR_0_S_AXI_HIGHADDR 0xDFFFFFFF


/* Peripheral Definitions for peripheral PSU_R5_0_ATCM_GLOBAL */
#define XPAR_PSU_R5_0_ATCM_GLOBAL_S_AXI_BASEADDR 0xFFE00000
#define XPAR_PSU_R5_0_ATCM_GLOBAL_S_AXI_HIGHADDR 0xFFE0FFFF


/* Peripheral Definitions for peripheral PSU_R5_0_BTCM_GLOBAL */
#define XPAR_PSU_R5_0_BTCM_GLOBAL_S_AXI_BASEADDR 0xFFE20000
#define XPAR_PSU_R5_0_BTCM_GLOBAL_S_AXI_HIGHADDR 0xFFE2FFFF


/* Peripheral Definitions for peripheral PSU_R5_1_ATCM_GLOBAL */
#define XPAR_PSU_R5_1_ATCM_GLOBAL_S_AXI_BASEADDR 0xFFE90000
#define XPAR_PSU_R5_1_ATCM_GLOBAL_S_AXI_HIGHADDR 0xFFE9FFFF


/* Peripheral Definitions for peripheral PSU_R5_1_BTCM_GLOBAL */
#define XPAR_PSU_R5_1_BTCM_GLOBAL_S_AXI_BASEADDR 0xFFEB0000
#define XPAR_PSU_R5_1_BTCM_GLOBAL_S_AXI_HIGHADDR 0xFFEBFFFF


/* Peripheral Definitions for peripheral PSU_R5_TCM_RAM_GLOBAL */
#define XPAR_PSU_R5_TCM_RAM_GLOBAL_S_AXI_BASEADDR 0xFFE00000
#define XPAR_PSU_R5_TCM_RAM_GLOBAL_S_AXI_HIGHADDR 0xFFE3FFFF


/* Peripheral Definitions for peripheral PSU_RPU */
#define XPAR_PSU_RPU_S_AXI_BASEADDR 0xFF9A0000
#define XPAR_PSU_RPU_S_AXI_HIGHADDR 0xFF9AFFFF


/* Peripheral Definitions for peripheral PSU_RSA */
#define XPAR_PSU_RSA_S_AXI_BASEADDR 0xFFCE0000
#define XPAR_PSU_RSA_S_AXI_HIGHADDR 0xFFCEFFFF


/* Peripheral Definitions for peripheral PSU_SERDES */
#define XPAR_PSU_SERDES_S_AXI_BASEADDR 0xFD400000
#define XPAR_PSU_SERDES_S_AXI_HIGHADDR 0xFD47FFFF


/* Peripheral Definitions for peripheral PSU_SIOU */
#define XPAR_PSU_SIOU_S_AXI_BASEADDR 0xFD3D0000
#define XPAR_PSU_SIOU_S_AXI_HIGHADDR 0xFD3DFFFF


/* Peripheral Definitions for peripheral PSU_SMMU_GPV */
#define XPAR_PSU_SMMU_GPV_S_AXI_BASEADDR 0xFD800000
#define XPAR_PSU_SMMU_GPV_S_AXI_HIGHADDR 0xFDFFFFFF


/* Peripheral Definitions for peripheral PSU_SMMU_REG */
#define XPAR_PSU_SMMU_REG_S_AXI_BASEADDR 0xFD5F0000
#define XPAR_PSU_SMMU_REG_S_AXI_HIGHADDR 0xFD5FFFFF


/******************************************************************/
















/* Canonical Definitions for peripheral PSU_APU */
#define XPAR_PSU_APU_0_S_AXI_BASEADDR 0xFD5C0000
#define XPAR_PSU_APU_0_S_AXI_HIGHADDR 0xFD5CFFFF


/* Canonical Definitions for peripheral PSU_CCI_GPV */
#define XPAR_PSU_CCI_GPV_0_S_AXI_BASEADDR 0xFD6E0000
#define XPAR_PSU_CCI_GPV_0_S_AXI_HIGHADDR 0xFD6EFFFF


/* Canonical Definitions for peripheral PSU_CCI_REG */
#define XPAR_PSU_CCI_REG_0_S_AXI_BASEADDR 0xFD5E0000
#define XPAR_PSU_CCI_REG_0_S_AXI_HIGHADDR 0xFD5EFFFF


/* Canonical Definitions for peripheral PSU_CRL_APB */
#define XPAR_PSU_CRL_APB_0_S_AXI_BASEADDR 0xFF5E0000
#define XPAR_PSU_CRL_APB_0_S_AXI_HIGHADDR 0xFF85FFFF




/* Canonical Definitions for peripheral PSU_CTRL_IPI */
#define XPAR_PERIPHERAL_0_S_AXI_BASEADDR 0xFF380000
#define XPAR_PERIPHERAL_0_S_AXI_HIGHADDR 0xFF3FFFFF






/* Canonical Definitions for peripheral PSU_DDR_PHY */
#define XPAR_PSU_DDR_PHY_0_S_AXI_BASEADDR 0xFD080000
#define XPAR_PSU_DDR_PHY_0_S_AXI_HIGHADDR 0xFD08FFFF


/* Canonical Definitions for peripheral PSU_DDR_QOS_CTRL */
#define XPAR_PSU_DDR_QOS_CTRL_0_S_AXI_BASEADDR 0xFD090000
#define XPAR_PSU_DDR_QOS_CTRL_0_S_AXI_HIGHADDR 0xFD09FFFF


/* Canonical Definitions for peripheral PSU_DDR_XMPU0_CFG */
#define XPAR_PSU_DDR_XMPU0_CFG_0_S_AXI_BASEADDR 0xFD000000
#define XPAR_PSU_DDR_XMPU0_CFG_0_S_AXI_HIGHADDR 0xFD00FFFF


/* Canonical Definitions for peripheral PSU_DDR_XMPU1_CFG */
#define XPAR_PSU_DDR_XMPU1_CFG_0_S_AXI_BASEADDR 0xFD010000
#define XPAR_PSU_DDR_XMPU1_CFG_0_S_AXI_HIGHADDR 0xFD01FFFF


/* Canonical Definitions for peripheral PSU_DDR_XMPU2_CFG */
#define XPAR_PSU_DDR_XMPU2_CFG_0_S_AXI_BASEADDR 0xFD020000
#define XPAR_PSU_DDR_XMPU2_CFG_0_S_AXI_HIGHADDR 0xFD02FFFF


/* Canonical Definitions for peripheral PSU_DDR_XMPU3_CFG */
#define XPAR_PSU_DDR_XMPU3_CFG_0_S_AXI_BASEADDR 0xFD030000
#define XPAR_PSU_DDR_XMPU3_CFG_0_S_AXI_HIGHADDR 0xFD03FFFF


/* Canonical Definitions for peripheral PSU_DDR_XMPU4_CFG */
#define XPAR_PSU_DDR_XMPU4_CFG_0_S_AXI_BASEADDR 0xFD040000
#define XPAR_PSU_DDR_XMPU4_CFG_0_S_AXI_HIGHADDR 0xFD04FFFF


/* Canonical Definitions for peripheral PSU_DDR_XMPU5_CFG */
#define XPAR_PSU_DDR_XMPU5_CFG_0_S_AXI_BASEADDR 0xFD050000
#define XPAR_PSU_DDR_XMPU5_CFG_0_S_AXI_HIGHADDR 0xFD05FFFF


/* Canonical Definitions for peripheral PSU_EFUSE */
#define XPAR_PSU_EFUSE_0_S_AXI_BASEADDR 0xFFCC0000
#define XPAR_PSU_EFUSE_0_S_AXI_HIGHADDR 0xFFCCFFFF


/* Canonical Definitions for peripheral PSU_FPD_GPV */
#define XPAR_PSU_FPD_GPV_0_S_AXI_BASEADDR 0xFD700000
#define XPAR_PSU_FPD_GPV_0_S_AXI_HIGHADDR 0xFD7FFFFF


/* Canonical Definitions for peripheral PSU_FPD_SLCR */
#define XPAR_PSU_FPD_SLCR_0_S_AXI_BASEADDR 0xFD610000
#define XPAR_PSU_FPD_SLCR_0_S_AXI_HIGHADDR 0xFD68FFFF


/* Canonical Definitions for peripheral PSU_FPD_SLCR_SECURE */
#define XPAR_PSU_FPD_SLCR_SECURE_0_S_AXI_BASEADDR 0xFD690000
#define XPAR_PSU_FPD_SLCR_SECURE_0_S_AXI_HIGHADDR 0xFD6CFFFF


/* Canonical Definitions for peripheral PSU_FPD_XMPU_CFG */
#define XPAR_PSU_FPD_XMPU_CFG_0_S_AXI_BASEADDR 0xFD5D0000
#define XPAR_PSU_FPD_XMPU_CFG_0_S_AXI_HIGHADDR 0xFD5DFFFF


/* Canonical Definitions for peripheral PSU_FPD_XMPU_SINK */
#define XPAR_PSU_FPD_XMPU_SINK_0_S_AXI_BASEADDR 0xFD4F0000
#define XPAR_PSU_FPD_XMPU_SINK_0_S_AXI_HIGHADDR 0xFD4FFFFF


/* Canonical Definitions for peripheral PSU_GPU */
#define XPAR_PSU_GPU_0_S_AXI_BASEADDR 0xFD4B0000
#define XPAR_PSU_GPU_0_S_AXI_HIGHADDR 0xFD4BFFFF


/* Canonical Definitions for peripheral PSU_IOU_SCNTR */
#define XPAR_PSU_IOU_SCNTR_0_S_AXI_BASEADDR 0xFF250000
#define XPAR_PSU_IOU_SCNTR_0_S_AXI_HIGHADDR 0xFF25FFFF


/* Canonical Definitions for peripheral PSU_IOU_SCNTRS */
#define XPAR_PSU_IOU_SCNTRS_0_S_AXI_BASEADDR 0xFF260000
#define XPAR_PSU_IOU_SCNTRS_0_S_AXI_HIGHADDR 0xFF26FFFF


/* Canonical Definitions for peripheral PSU_IOUSECURE_SLCR */
#define XPAR_PSU_IOUSECURE_SLCR_0_S_AXI_BASEADDR 0xFF240000
#define XPAR_PSU_IOUSECURE_SLCR_0_S_AXI_HIGHADDR 0xFF24FFFF




/* Canonical Definitions for peripheral PSU_LPD_SLCR */
#define XPAR_PSU_LPD_SLCR_0_S_AXI_BASEADDR 0xFF410000
#define XPAR_PSU_LPD_SLCR_0_S_AXI_HIGHADDR 0xFF4AFFFF


/* Canonical Definitions for peripheral PSU_LPD_SLCR_SECURE */
#define XPAR_PSU_LPD_SLCR_SECURE_0_S_AXI_BASEADDR 0xFF4B0000
#define XPAR_PSU_LPD_SLCR_SECURE_0_S_AXI_HIGHADDR 0xFF4DFFFF


/* Canonical Definitions for peripheral PSU_LPD_XPPU */
#define XPAR_PSU_LPD_XPPU_0_S_AXI_BASEADDR 0xFF980000
#define XPAR_PSU_LPD_XPPU_0_S_AXI_HIGHADDR 0xFF99FFFF


/* Canonical Definitions for peripheral PSU_LPD_XPPU_SINK */
#define XPAR_PSU_LPD_XPPU_SINK_0_S_AXI_BASEADDR 0xFF9C0000
#define XPAR_PSU_LPD_XPPU_SINK_0_S_AXI_HIGHADDR 0xFF9CFFFF


/* Canonical Definitions for peripheral PSU_MBISTJTAG */
#define XPAR_PSU_MBISTJTAG_0_S_AXI_BASEADDR 0xFFCF0000
#define XPAR_PSU_MBISTJTAG_0_S_AXI_HIGHADDR 0xFFCFFFFF


/* Canonical Definitions for peripheral PSU_MESSAGE_BUFFERS */
#define XPAR_PERIPHERAL_1_S_AXI_BASEADDR 0xFF990000
#define XPAR_PERIPHERAL_1_S_AXI_HIGHADDR 0xFF99FFFF


/* Canonical Definitions for peripheral PSU_OCM */
#define XPAR_PSU_OCM_0_S_AXI_BASEADDR 0xFF960000
#define XPAR_PSU_OCM_0_S_AXI_HIGHADDR 0xFF96FFFF




/* Canonical Definitions for peripheral PSU_OCM_XMPU_CFG */
#define XPAR_PSU_OCM_XMPU_CFG_0_S_AXI_BASEADDR 0xFFA70000
#define XPAR_PSU_OCM_XMPU_CFG_0_S_AXI_HIGHADDR 0xFFA7FFFF






/* Canonical Definitions for peripheral PSU_R5_0_ATCM_GLOBAL */
#define XPAR_PSU_R5_0_ATCM_GLOBAL_0_S_AXI_BASEADDR 0xFFE00000
#define XPAR_PSU_R5_0_ATCM_GLOBAL_0_S_AXI_HIGHADDR 0xFFE0FFFF


/* Canonical Definitions for peripheral PSU_R5_0_BTCM_GLOBAL */
#define XPAR_PSU_R5_0_BTCM_GLOBAL_0_S_AXI_BASEADDR 0xFFE20000
#define XPAR_PSU_R5_0_BTCM_GLOBAL_0_S_AXI_HIGHADDR 0xFFE2FFFF


/* Canonical Definitions for peripheral PSU_R5_1_ATCM_GLOBAL */
#define XPAR_PSU_R5_1_ATCM_GLOBAL_0_S_AXI_BASEADDR 0xFFE90000
#define XPAR_PSU_R5_1_ATCM_GLOBAL_0_S_AXI_HIGHADDR 0xFFE9FFFF


/* Canonical Definitions for peripheral PSU_R5_1_BTCM_GLOBAL */
#define XPAR_PSU_R5_1_BTCM_GLOBAL_0_S_AXI_BASEADDR 0xFFEB0000
#define XPAR_PSU_R5_1_BTCM_GLOBAL_0_S_AXI_HIGHADDR 0xFFEBFFFF


/* Canonical Definitions for peripheral PSU_R5_TCM_RAM_GLOBAL */
#define XPAR_PSU_R5_TCM_RAM_0_S_AXI_BASEADDR 0xFFE00000
#define XPAR_PSU_R5_TCM_RAM_0_S_AXI_HIGHADDR 0xFFE3FFFF


/* Canonical Definitions for peripheral PSU_RPU */
#define XPAR_PSU_RPU_0_S_AXI_BASEADDR 0xFF9A0000
#define XPAR_PSU_RPU_0_S_AXI_HIGHADDR 0xFF9AFFFF


/* Canonical Definitions for peripheral PSU_RSA */
#define XPAR_PSU_RSA_0_S_AXI_BASEADDR 0xFFCE0000
#define XPAR_PSU_RSA_0_S_AXI_HIGHADDR 0xFFCEFFFF


/* Canonical Definitions for peripheral PSU_SERDES */
#define XPAR_PSU_SERDES_0_S_AXI_BASEADDR 0xFD400000
#define XPAR_PSU_SERDES_0_S_AXI_HIGHADDR 0xFD47FFFF


/* Canonical Definitions for peripheral PSU_SIOU */
#define XPAR_PSU_SIOU_0_S_AXI_BASEADDR 0xFD3D0000
#define XPAR_PSU_SIOU_0_S_AXI_HIGHADDR 0xFD3DFFFF


/* Canonical Definitions for peripheral PSU_SMMU_GPV */
#define XPAR_PSU_SMMU_GPV_0_S_AXI_BASEADDR 0xFD800000
#define XPAR_PSU_SMMU_GPV_0_S_AXI_HIGHADDR 0xFDFFFFFF


/* Canonical Definitions for peripheral PSU_SMMU_REG */
#define XPAR_PSU_SMMU_REG_0_S_AXI_BASEADDR 0xFD5F0000
#define XPAR_PSU_SMMU_REG_0_S_AXI_HIGHADDR 0xFD5FFFFF


/******************************************************************/

/* Definitions for driver GPIOPS */
#define XPAR_XGPIOPS_NUM_INSTANCES 1

/* Definitions for peripheral PSU_GPIO_0 */
#define XPAR_PSU_GPIO_0_DEVICE_ID 0
#define XPAR_PSU_GPIO_0_BASEADDR 0xFF0A0000
#define XPAR_PSU_GPIO_0_HIGHADDR 0xFF0AFFFF


/******************************************************************/

/* Canonical definitions for peripheral PSU_GPIO_0 */
#define XPAR_XGPIOPS_0_DEVICE_ID XPAR_PSU_GPIO_0_DEVICE_ID
#define XPAR_XGPIOPS_0_BASEADDR 0xFF0A0000
#define XPAR_XGPIOPS_0_HIGHADDR 0xFF0AFFFF


/******************************************************************/

/* Definitions for driver IICPS */
#define XPAR_XIICPS_NUM_INSTANCES 1

/* Definitions for peripheral PSU_I2C_1 */
#define XPAR_PSU_I2C_1_DEVICE_ID 0
#define XPAR_PSU_I2C_1_BASEADDR 0xFF030000
#define XPAR_PSU_I2C_1_HIGHADDR 0xFF03FFFF
#define XPAR_PSU_I2C_1_I2C_CLK_FREQ_HZ 99999001


/******************************************************************/

/* Canonical definitions for peripheral PSU_I2C_1 */
#define XPAR_XIICPS_0_DEVICE_ID XPAR_PSU_I2C_1_DEVICE_ID
#define XPAR_XIICPS_0_BASEADDR 0xFF030000
#define XPAR_XIICPS_0_HIGHADDR 0xFF03FFFF
#define XPAR_XIICPS_0_I2C_CLK_FREQ_HZ 99999001


/******************************************************************/

/* Definition for input Clock */
#define XPAR_PSU_I2C_1_REF_CLK I2C1_REF
#define  XPAR_XIPIPSU_NUM_INSTANCES  1U

/* Parameter definitions for peripheral psu_ipi_0 */
#define  XPAR_PSU_IPI_0_DEVICE_ID  0U
#define  XPAR_PSU_IPI_0_S_AXI_BASEADDR  0xFF300000U
#define  XPAR_PSU_IPI_0_BIT_MASK  0x00000001U
#define  XPAR_PSU_IPI_0_BUFFER_INDEX  2U
#define  XPAR_PSU_IPI_0_INT_ID  67U

/* Canonical definitions for peripheral psu_ipi_0 */
#define  XPAR_XIPIPSU_0_DEVICE_ID	XPAR_PSU_IPI_0_DEVICE_ID
#define  XPAR_XIPIPSU_0_BASE_ADDRESS	XPAR_PSU_IPI_0_S_AXI_BASEADDR
#define  XPAR_XIPIPSU_0_BIT_MASK	XPAR_PSU_IPI_0_BIT_MASK
#define  XPAR_XIPIPSU_0_BUFFER_INDEX	XPAR_PSU_IPI_0_BUFFER_INDEX
#define  XPAR_XIPIPSU_0_INT_ID	XPAR_PSU_IPI_0_INT_ID

#define  XPAR_XIPIPSU_NUM_TARGETS  7U

#define  XPAR_PSU_IPI_0_BIT_MASK  0x00000001U
#define  XPAR_PSU_IPI_0_BUFFER_INDEX  2U
#define  XPAR_PSU_IPI_1_BIT_MASK  0x00000100U
#define  XPAR_PSU_IPI_1_BUFFER_INDEX  0U
#define  XPAR_PSU_IPI_2_BIT_MASK  0x00000200U
#define  XPAR_PSU_IPI_2_BUFFER_INDEX  1U
#define  XPAR_PSU_IPI_3_BIT_MASK  0x00010000U
#define  XPAR_PSU_IPI_3_BUFFER_INDEX  7U
#define  XPAR_PSU_IPI_4_BIT_MASK  0x00020000U
#define  XPAR_PSU_IPI_4_BUFFER_INDEX  7U
#define  XPAR_PSU_IPI_5_BIT_MASK  0x00040000U
#define  XPAR_PSU_IPI_5_BUFFER_INDEX  7U
#define  XPAR_PSU_IPI_6_BIT_MASK  0x00080000U
#define  XPAR_PSU_IPI_6_BUFFER_INDEX  7U
/* Target List for referring to processor IPI Targets */

#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_0_CH0_MASK  XPAR_PSU_IPI_0_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_0_CH0_INDEX  0U

#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_1_CH0_MASK  XPAR_PSU_IPI_0_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_1_CH0_INDEX  0U

#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_2_CH0_MASK  XPAR_PSU_IPI_0_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_2_CH0_INDEX  0U

#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_3_CH0_MASK  XPAR_PSU_IPI_0_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_CORTEXA53_3_CH0_INDEX  0U

#define  XPAR_XIPIPS_TARGET_PSU_CORTEXR5_0_CH0_MASK  XPAR_PSU_IPI_1_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_CORTEXR5_0_CH0_INDEX  1U

#define  XPAR_XIPIPS_TARGET_PSU_CORTEXR5_1_CH0_MASK  XPAR_PSU_IPI_2_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_CORTEXR5_1_CH0_INDEX  2U

#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH0_MASK  XPAR_PSU_IPI_3_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH0_INDEX  3U
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH1_MASK  XPAR_PSU_IPI_4_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH1_INDEX  4U
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH2_MASK  XPAR_PSU_IPI_5_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH2_INDEX  5U
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH3_MASK  XPAR_PSU_IPI_6_BIT_MASK
#define  XPAR_XIPIPS_TARGET_PSU_PMU_0_CH3_INDEX  6U

/* Definitions for driver QSPIPSU */
#define XPAR_XQSPIPSU_NUM_INSTANCES 1

/* Definitions for peripheral PSU_QSPI_0 */
#define XPAR_PSU_QSPI_0_DEVICE_ID 0
#define XPAR_PSU_QSPI_0_BASEADDR 0xFF0F0000
#define XPAR_PSU_QSPI_0_HIGHADDR 0xFF0FFFFF
#define XPAR_PSU_QSPI_0_QSPI_CLK_FREQ_HZ 124998749
#define XPAR_PSU_QSPI_0_QSPI_MODE 0
#define XPAR_PSU_QSPI_0_QSPI_BUS_WIDTH 2


/******************************************************************/

#define XPAR_PSU_QSPI_0_IS_CACHE_COHERENT 0
#define XPAR_PSU_QSPI_0_REF_CLK QSPI_REF
/* Canonical definitions for peripheral PSU_QSPI_0 */
#define XPAR_XQSPIPSU_0_DEVICE_ID XPAR_PSU_QSPI_0_DEVICE_ID
#define XPAR_XQSPIPSU_0_BASEADDR 0xFF0F0000
#define XPAR_XQSPIPSU_0_HIGHADDR 0xFF0FFFFF
#define XPAR_XQSPIPSU_0_QSPI_CLK_FREQ_HZ 124998749
#define XPAR_XQSPIPSU_0_QSPI_MODE 0
#define XPAR_XQSPIPSU_0_QSPI_BUS_WIDTH 2
#define XPAR_XQSPIPSU_0_IS_CACHE_COHERENT 0


/******************************************************************/

/* Definitions for driver RESETPS and CLOCKPS */
#define XPAR_XCRPSU_NUM_INSTANCES 1U

/* Definitions for peripheral PSU_CR_0 */
#define XPAR_PSU_CR_DEVICE_ID 0

/******************************************************************/

/* Definitions for peripheral PSU_CRF_APB */
#define XPAR_PSU_CRF_APB_S_AXI_BASEADDR 0xFD1A0000
#define XPAR_PSU_CRF_APB_S_AXI_HIGHADDR 0xFD2DFFFF


/******************************************************************/

/* Canonical definitions for peripheral PSU_CR_0 */
#define XPAR_XCRPSU_0_DEVICE_ID 0

/******************************************************************/


/* Definitions for peripheral PSU_PMU_IOMODULE */
#define XPAR_PSU_PMU_IOMODULE_S_AXI_BASEADDR 0xFFD40000
#define XPAR_PSU_PMU_IOMODULE_S_AXI_HIGHADDR 0xFFD5FFFF


/* Definitions for peripheral PSU_LPD_SLCR */
#define XPAR_PSU_LPD_SLCR_S_AXI_BASEADDR 0xFF410000
#define XPAR_PSU_LPD_SLCR_S_AXI_HIGHADDR 0xFF4AFFFF


/******************************************************************/

/* Definitions for driver RTCPSU */
#define XPAR_XRTCPSU_NUM_INSTANCES 1

/* Definitions for peripheral PSU_RTC */
#define XPAR_PSU_RTC_DEVICE_ID 0
#define XPAR_PSU_RTC_BASEADDR 0xFFA60000
#define XPAR_PSU_RTC_HIGHADDR 0xFFA6FFFF


/******************************************************************/

/* Canonical definitions for peripheral PSU_RTC */
#define XPAR_XRTCPSU_0_DEVICE_ID XPAR_PSU_RTC_DEVICE_ID
#define XPAR_XRTCPSU_0_BASEADDR 0xFFA60000
#define XPAR_XRTCPSU_0_HIGHADDR 0xFFA6FFFF


/******************************************************************/

/* Definitions for Fabric interrupts connected to psu_acpu_gic */
#define XPAR_FABRIC_PL_PS_IRQ0_0_INTR 121U

/******************************************************************/

/* Canonical definitions for Fabric interrupts connected to psu_acpu_gic */

/******************************************************************/

/* Definitions for driver SCUGIC */
#define XPAR_XSCUGIC_NUM_INSTANCES 1U

/* Definitions for peripheral PSU_ACPU_GIC */
#define XPAR_PSU_ACPU_GIC_DEVICE_ID 0U
#define XPAR_PSU_ACPU_GIC_BASEADDR 0xF9020000U
#define XPAR_PSU_ACPU_GIC_HIGHADDR 0xF9020FFFU
#define XPAR_PSU_ACPU_GIC_DIST_BASEADDR 0xF9010000U


/******************************************************************/

/* Canonical definitions for peripheral PSU_ACPU_GIC */
#define XPAR_SCUGIC_0_DEVICE_ID 0U
#define XPAR_SCUGIC_0_CPU_BASEADDR 0xF9020000U
#define XPAR_SCUGIC_0_CPU_HIGHADDR 0xF9020FFFU
#define XPAR_SCUGIC_0_DIST_BASEADDR 0xF9010000U


/******************************************************************/

/* Definitions for driver SPIPS */
#define XPAR_XSPIPS_NUM_INSTANCES 1

/* Definitions for peripheral PSU_SPI_1 */
#define XPAR_PSU_SPI_1_DEVICE_ID 0
#define XPAR_PSU_SPI_1_BASEADDR 0xFF050000
#define XPAR_PSU_SPI_1_HIGHADDR 0xFF05FFFF
#define XPAR_PSU_SPI_1_SPI_CLK_FREQ_HZ 199998001


/******************************************************************/

/* Canonical definitions for peripheral PSU_SPI_1 */
#define XPAR_XSPIPS_0_DEVICE_ID XPAR_PSU_SPI_1_DEVICE_ID
#define XPAR_XSPIPS_0_BASEADDR 0xFF050000
#define XPAR_XSPIPS_0_HIGHADDR 0xFF05FFFF
#define XPAR_XSPIPS_0_SPI_CLK_FREQ_HZ 199998001


/******************************************************************/

/* Definitions for driver SYSMONPSU */
#define XPAR_XSYSMONPSU_NUM_INSTANCES 1

/* Definitions for peripheral PSU_AMS */
#define XPAR_PSU_AMS_DEVICE_ID 0
#define XPAR_PSU_AMS_BASEADDR 0xFFA50000
#define XPAR_PSU_AMS_HIGHADDR 0xFFA5FFFF


/******************************************************************/

#define XPAR_PSU_AMS_REF_FREQMHZ 49.999500
/* Canonical definitions for peripheral PSU_AMS */
#define XPAR_XSYSMONPSU_0_DEVICE_ID XPAR_PSU_AMS_DEVICE_ID
#define XPAR_XSYSMONPSU_0_BASEADDR 0xFFA50000
#define XPAR_XSYSMONPSU_0_HIGHADDR 0xFFA5FFFF


/******************************************************************/

#define XPAR_XSYSMONPSU_0_REF_FREQMHZ 49.999500
/* Definitions for driver TTCPS */
#define XPAR_XTTCPS_NUM_INSTANCES 12U

/* Definitions for peripheral PSU_TTC_0 */
#define XPAR_PSU_TTC_0_DEVICE_ID 0U
#define XPAR_PSU_TTC_0_BASEADDR 0XFF110000U
#define XPAR_PSU_TTC_0_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_0_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_1_DEVICE_ID 1U
#define XPAR_PSU_TTC_1_BASEADDR 0XFF110004U
#define XPAR_PSU_TTC_1_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_1_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_2_DEVICE_ID 2U
#define XPAR_PSU_TTC_2_BASEADDR 0XFF110008U
#define XPAR_PSU_TTC_2_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_2_TTC_CLK_CLKSRC 0U


/* Definitions for peripheral PSU_TTC_1 */
#define XPAR_PSU_TTC_3_DEVICE_ID 3U
#define XPAR_PSU_TTC_3_BASEADDR 0XFF120000U
#define XPAR_PSU_TTC_3_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_3_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_4_DEVICE_ID 4U
#define XPAR_PSU_TTC_4_BASEADDR 0XFF120004U
#define XPAR_PSU_TTC_4_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_4_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_5_DEVICE_ID 5U
#define XPAR_PSU_TTC_5_BASEADDR 0XFF120008U
#define XPAR_PSU_TTC_5_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_5_TTC_CLK_CLKSRC 0U


/* Definitions for peripheral PSU_TTC_2 */
#define XPAR_PSU_TTC_6_DEVICE_ID 6U
#define XPAR_PSU_TTC_6_BASEADDR 0XFF130000U
#define XPAR_PSU_TTC_6_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_6_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_7_DEVICE_ID 7U
#define XPAR_PSU_TTC_7_BASEADDR 0XFF130004U
#define XPAR_PSU_TTC_7_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_7_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_8_DEVICE_ID 8U
#define XPAR_PSU_TTC_8_BASEADDR 0XFF130008U
#define XPAR_PSU_TTC_8_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_8_TTC_CLK_CLKSRC 0U


/* Definitions for peripheral PSU_TTC_3 */
#define XPAR_PSU_TTC_9_DEVICE_ID 9U
#define XPAR_PSU_TTC_9_BASEADDR 0XFF140000U
#define XPAR_PSU_TTC_9_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_9_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_10_DEVICE_ID 10U
#define XPAR_PSU_TTC_10_BASEADDR 0XFF140004U
#define XPAR_PSU_TTC_10_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_10_TTC_CLK_CLKSRC 0U
#define XPAR_PSU_TTC_11_DEVICE_ID 11U
#define XPAR_PSU_TTC_11_BASEADDR 0XFF140008U
#define XPAR_PSU_TTC_11_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_PSU_TTC_11_TTC_CLK_CLKSRC 0U


/******************************************************************/

/* Canonical definitions for peripheral PSU_TTC_0 */
#define XPAR_XTTCPS_0_DEVICE_ID XPAR_PSU_TTC_0_DEVICE_ID
#define XPAR_XTTCPS_0_BASEADDR 0xFF110000U
#define XPAR_XTTCPS_0_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_0_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_1_DEVICE_ID XPAR_PSU_TTC_1_DEVICE_ID
#define XPAR_XTTCPS_1_BASEADDR 0xFF110004U
#define XPAR_XTTCPS_1_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_1_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_2_DEVICE_ID XPAR_PSU_TTC_2_DEVICE_ID
#define XPAR_XTTCPS_2_BASEADDR 0xFF110008U
#define XPAR_XTTCPS_2_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_2_TTC_CLK_CLKSRC 0U

/* Canonical definitions for peripheral PSU_TTC_1 */
#define XPAR_XTTCPS_3_DEVICE_ID XPAR_PSU_TTC_3_DEVICE_ID
#define XPAR_XTTCPS_3_BASEADDR 0xFF120000U
#define XPAR_XTTCPS_3_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_3_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_4_DEVICE_ID XPAR_PSU_TTC_4_DEVICE_ID
#define XPAR_XTTCPS_4_BASEADDR 0xFF120004U
#define XPAR_XTTCPS_4_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_4_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_5_DEVICE_ID XPAR_PSU_TTC_5_DEVICE_ID
#define XPAR_XTTCPS_5_BASEADDR 0xFF120008U
#define XPAR_XTTCPS_5_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_5_TTC_CLK_CLKSRC 0U

/* Canonical definitions for peripheral PSU_TTC_2 */
#define XPAR_XTTCPS_6_DEVICE_ID XPAR_PSU_TTC_6_DEVICE_ID
#define XPAR_XTTCPS_6_BASEADDR 0xFF130000U
#define XPAR_XTTCPS_6_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_6_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_7_DEVICE_ID XPAR_PSU_TTC_7_DEVICE_ID
#define XPAR_XTTCPS_7_BASEADDR 0xFF130004U
#define XPAR_XTTCPS_7_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_7_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_8_DEVICE_ID XPAR_PSU_TTC_8_DEVICE_ID
#define XPAR_XTTCPS_8_BASEADDR 0xFF130008U
#define XPAR_XTTCPS_8_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_8_TTC_CLK_CLKSRC 0U

/* Canonical definitions for peripheral PSU_TTC_3 */
#define XPAR_XTTCPS_9_DEVICE_ID XPAR_PSU_TTC_9_DEVICE_ID
#define XPAR_XTTCPS_9_BASEADDR 0xFF140000U
#define XPAR_XTTCPS_9_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_9_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_10_DEVICE_ID XPAR_PSU_TTC_10_DEVICE_ID
#define XPAR_XTTCPS_10_BASEADDR 0xFF140004U
#define XPAR_XTTCPS_10_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_10_TTC_CLK_CLKSRC 0U

#define XPAR_XTTCPS_11_DEVICE_ID XPAR_PSU_TTC_11_DEVICE_ID
#define XPAR_XTTCPS_11_BASEADDR 0xFF140008U
#define XPAR_XTTCPS_11_TTC_CLK_FREQ_HZ 100000000U
#define XPAR_XTTCPS_11_TTC_CLK_CLKSRC 0U


/******************************************************************/

/* Definitions for driver UARTPS */
#define XPAR_XUARTPS_NUM_INSTANCES 1

/* Definitions for peripheral PSU_UART_1 */
#define XPAR_PSU_UART_1_DEVICE_ID 0
#define XPAR_PSU_UART_1_BASEADDR 0xFF010000
#define XPAR_PSU_UART_1_HIGHADDR 0xFF01FFFF
#define XPAR_PSU_UART_1_UART_CLK_FREQ_HZ 99999001
#define XPAR_PSU_UART_1_HAS_MODEM 0


/******************************************************************/

/* Canonical definitions for peripheral PSU_UART_1 */
#define XPAR_XUARTPS_0_DEVICE_ID XPAR_PSU_UART_1_DEVICE_ID
#define XPAR_XUARTPS_0_BASEADDR 0xFF010000
#define XPAR_XUARTPS_0_HIGHADDR 0xFF01FFFF
#define XPAR_XUARTPS_0_UART_CLK_FREQ_HZ 99999001
#define XPAR_XUARTPS_0_HAS_MODEM 0


/******************************************************************/

/* Definition for input Clock */
#define XPAR_PSU_UART_1_REF_CLK UART1_REF
/* Definitions for driver WDTPS */
#define XPAR_XWDTPS_NUM_INSTANCES 2

/* Definitions for peripheral PSU_WDT_0 */
#define XPAR_PSU_WDT_0_DEVICE_ID 0
#define XPAR_PSU_WDT_0_BASEADDR 0xFF150000
#define XPAR_PSU_WDT_0_HIGHADDR 0xFF15FFFF
#define XPAR_PSU_WDT_0_WDT_CLK_FREQ_HZ 99999001


/* Definitions for peripheral PSU_WDT_1 */
#define XPAR_PSU_WDT_1_DEVICE_ID 1
#define XPAR_PSU_WDT_1_BASEADDR 0xFD4D0000
#define XPAR_PSU_WDT_1_HIGHADDR 0xFD4DFFFF
#define XPAR_PSU_WDT_1_WDT_CLK_FREQ_HZ 99999001


/******************************************************************/

/* Canonical definitions for peripheral PSU_WDT_0 */
#define XPAR_XWDTPS_0_DEVICE_ID XPAR_PSU_WDT_0_DEVICE_ID
#define XPAR_XWDTPS_0_BASEADDR 0xFF150000
#define XPAR_XWDTPS_0_HIGHADDR 0xFF15FFFF
#define XPAR_XWDTPS_0_WDT_CLK_FREQ_HZ 99999001

/* Canonical definitions for peripheral PSU_WDT_1 */
#define XPAR_XWDTPS_1_DEVICE_ID XPAR_PSU_WDT_1_DEVICE_ID
#define XPAR_XWDTPS_1_BASEADDR 0xFD4D0000
#define XPAR_XWDTPS_1_HIGHADDR 0xFD4DFFFF
#define XPAR_XWDTPS_1_WDT_CLK_FREQ_HZ 99999001


/******************************************************************/

/* Definitions for driver ZDMA */
#define XPAR_XZDMA_NUM_INSTANCES 16

/* Definitions for peripheral PSU_ADMA_0 */
#define XPAR_PSU_ADMA_0_DEVICE_ID 0
#define XPAR_PSU_ADMA_0_BASEADDR 0xFFA80000
#define XPAR_PSU_ADMA_0_DMA_MODE 1
#define XPAR_PSU_ADMA_0_HIGHADDR 0xFFA8FFFF
#define XPAR_PSU_ADMA_0_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_1 */
#define XPAR_PSU_ADMA_1_DEVICE_ID 1
#define XPAR_PSU_ADMA_1_BASEADDR 0xFFA90000
#define XPAR_PSU_ADMA_1_DMA_MODE 1
#define XPAR_PSU_ADMA_1_HIGHADDR 0xFFA9FFFF
#define XPAR_PSU_ADMA_1_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_2 */
#define XPAR_PSU_ADMA_2_DEVICE_ID 2
#define XPAR_PSU_ADMA_2_BASEADDR 0xFFAA0000
#define XPAR_PSU_ADMA_2_DMA_MODE 1
#define XPAR_PSU_ADMA_2_HIGHADDR 0xFFAAFFFF
#define XPAR_PSU_ADMA_2_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_3 */
#define XPAR_PSU_ADMA_3_DEVICE_ID 3
#define XPAR_PSU_ADMA_3_BASEADDR 0xFFAB0000
#define XPAR_PSU_ADMA_3_DMA_MODE 1
#define XPAR_PSU_ADMA_3_HIGHADDR 0xFFABFFFF
#define XPAR_PSU_ADMA_3_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_4 */
#define XPAR_PSU_ADMA_4_DEVICE_ID 4
#define XPAR_PSU_ADMA_4_BASEADDR 0xFFAC0000
#define XPAR_PSU_ADMA_4_DMA_MODE 1
#define XPAR_PSU_ADMA_4_HIGHADDR 0xFFACFFFF
#define XPAR_PSU_ADMA_4_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_5 */
#define XPAR_PSU_ADMA_5_DEVICE_ID 5
#define XPAR_PSU_ADMA_5_BASEADDR 0xFFAD0000
#define XPAR_PSU_ADMA_5_DMA_MODE 1
#define XPAR_PSU_ADMA_5_HIGHADDR 0xFFADFFFF
#define XPAR_PSU_ADMA_5_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_6 */
#define XPAR_PSU_ADMA_6_DEVICE_ID 6
#define XPAR_PSU_ADMA_6_BASEADDR 0xFFAE0000
#define XPAR_PSU_ADMA_6_DMA_MODE 1
#define XPAR_PSU_ADMA_6_HIGHADDR 0xFFAEFFFF
#define XPAR_PSU_ADMA_6_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_ADMA_7 */
#define XPAR_PSU_ADMA_7_DEVICE_ID 7
#define XPAR_PSU_ADMA_7_BASEADDR 0xFFAF0000
#define XPAR_PSU_ADMA_7_DMA_MODE 1
#define XPAR_PSU_ADMA_7_HIGHADDR 0xFFAFFFFF
#define XPAR_PSU_ADMA_7_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_0 */
#define XPAR_PSU_GDMA_0_DEVICE_ID 8
#define XPAR_PSU_GDMA_0_BASEADDR 0xFD500000
#define XPAR_PSU_GDMA_0_DMA_MODE 0
#define XPAR_PSU_GDMA_0_HIGHADDR 0xFD50FFFF
#define XPAR_PSU_GDMA_0_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_1 */
#define XPAR_PSU_GDMA_1_DEVICE_ID 9
#define XPAR_PSU_GDMA_1_BASEADDR 0xFD510000
#define XPAR_PSU_GDMA_1_DMA_MODE 0
#define XPAR_PSU_GDMA_1_HIGHADDR 0xFD51FFFF
#define XPAR_PSU_GDMA_1_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_2 */
#define XPAR_PSU_GDMA_2_DEVICE_ID 10
#define XPAR_PSU_GDMA_2_BASEADDR 0xFD520000
#define XPAR_PSU_GDMA_2_DMA_MODE 0
#define XPAR_PSU_GDMA_2_HIGHADDR 0xFD52FFFF
#define XPAR_PSU_GDMA_2_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_3 */
#define XPAR_PSU_GDMA_3_DEVICE_ID 11
#define XPAR_PSU_GDMA_3_BASEADDR 0xFD530000
#define XPAR_PSU_GDMA_3_DMA_MODE 0
#define XPAR_PSU_GDMA_3_HIGHADDR 0xFD53FFFF
#define XPAR_PSU_GDMA_3_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_4 */
#define XPAR_PSU_GDMA_4_DEVICE_ID 12
#define XPAR_PSU_GDMA_4_BASEADDR 0xFD540000
#define XPAR_PSU_GDMA_4_DMA_MODE 0
#define XPAR_PSU_GDMA_4_HIGHADDR 0xFD54FFFF
#define XPAR_PSU_GDMA_4_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_5 */
#define XPAR_PSU_GDMA_5_DEVICE_ID 13
#define XPAR_PSU_GDMA_5_BASEADDR 0xFD550000
#define XPAR_PSU_GDMA_5_DMA_MODE 0
#define XPAR_PSU_GDMA_5_HIGHADDR 0xFD55FFFF
#define XPAR_PSU_GDMA_5_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_6 */
#define XPAR_PSU_GDMA_6_DEVICE_ID 14
#define XPAR_PSU_GDMA_6_BASEADDR 0xFD560000
#define XPAR_PSU_GDMA_6_DMA_MODE 0
#define XPAR_PSU_GDMA_6_HIGHADDR 0xFD56FFFF
#define XPAR_PSU_GDMA_6_ZDMA_CLK_FREQ_HZ 0


/* Definitions for peripheral PSU_GDMA_7 */
#define XPAR_PSU_GDMA_7_DEVICE_ID 15
#define XPAR_PSU_GDMA_7_BASEADDR 0xFD570000
#define XPAR_PSU_GDMA_7_DMA_MODE 0
#define XPAR_PSU_GDMA_7_HIGHADDR 0xFD57FFFF
#define XPAR_PSU_GDMA_7_ZDMA_CLK_FREQ_HZ 0


/******************************************************************/

#define XPAR_PSU_ADMA_0_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_1_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_2_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_3_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_4_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_5_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_6_IS_CACHE_COHERENT 0
#define XPAR_PSU_ADMA_7_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_0_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_1_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_2_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_3_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_4_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_5_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_6_IS_CACHE_COHERENT 0
#define XPAR_PSU_GDMA_7_IS_CACHE_COHERENT 0
/* Canonical definitions for peripheral PSU_ADMA_0 */
#define XPAR_XZDMA_0_DEVICE_ID XPAR_PSU_ADMA_0_DEVICE_ID
#define XPAR_XZDMA_0_BASEADDR 0xFFA80000
#define XPAR_XZDMA_0_DMA_MODE 1
#define XPAR_XZDMA_0_HIGHADDR 0xFFA8FFFF
#define XPAR_XZDMA_0_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_1 */
#define XPAR_XZDMA_1_DEVICE_ID XPAR_PSU_ADMA_1_DEVICE_ID
#define XPAR_XZDMA_1_BASEADDR 0xFFA90000
#define XPAR_XZDMA_1_DMA_MODE 1
#define XPAR_XZDMA_1_HIGHADDR 0xFFA9FFFF
#define XPAR_XZDMA_1_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_2 */
#define XPAR_XZDMA_2_DEVICE_ID XPAR_PSU_ADMA_2_DEVICE_ID
#define XPAR_XZDMA_2_BASEADDR 0xFFAA0000
#define XPAR_XZDMA_2_DMA_MODE 1
#define XPAR_XZDMA_2_HIGHADDR 0xFFAAFFFF
#define XPAR_XZDMA_2_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_3 */
#define XPAR_XZDMA_3_DEVICE_ID XPAR_PSU_ADMA_3_DEVICE_ID
#define XPAR_XZDMA_3_BASEADDR 0xFFAB0000
#define XPAR_XZDMA_3_DMA_MODE 1
#define XPAR_XZDMA_3_HIGHADDR 0xFFABFFFF
#define XPAR_XZDMA_3_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_4 */
#define XPAR_XZDMA_4_DEVICE_ID XPAR_PSU_ADMA_4_DEVICE_ID
#define XPAR_XZDMA_4_BASEADDR 0xFFAC0000
#define XPAR_XZDMA_4_DMA_MODE 1
#define XPAR_XZDMA_4_HIGHADDR 0xFFACFFFF
#define XPAR_XZDMA_4_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_5 */
#define XPAR_XZDMA_5_DEVICE_ID XPAR_PSU_ADMA_5_DEVICE_ID
#define XPAR_XZDMA_5_BASEADDR 0xFFAD0000
#define XPAR_XZDMA_5_DMA_MODE 1
#define XPAR_XZDMA_5_HIGHADDR 0xFFADFFFF
#define XPAR_XZDMA_5_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_6 */
#define XPAR_XZDMA_6_DEVICE_ID XPAR_PSU_ADMA_6_DEVICE_ID
#define XPAR_XZDMA_6_BASEADDR 0xFFAE0000
#define XPAR_XZDMA_6_DMA_MODE 1
#define XPAR_XZDMA_6_HIGHADDR 0xFFAEFFFF
#define XPAR_XZDMA_6_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_ADMA_7 */
#define XPAR_XZDMA_7_DEVICE_ID XPAR_PSU_ADMA_7_DEVICE_ID
#define XPAR_XZDMA_7_BASEADDR 0xFFAF0000
#define XPAR_XZDMA_7_DMA_MODE 1
#define XPAR_XZDMA_7_HIGHADDR 0xFFAFFFFF
#define XPAR_XZDMA_7_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_0 */
#define XPAR_XZDMA_8_DEVICE_ID XPAR_PSU_GDMA_0_DEVICE_ID
#define XPAR_XZDMA_8_BASEADDR 0xFD500000
#define XPAR_XZDMA_8_DMA_MODE 0
#define XPAR_XZDMA_8_HIGHADDR 0xFD50FFFF
#define XPAR_XZDMA_8_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_1 */
#define XPAR_XZDMA_9_DEVICE_ID XPAR_PSU_GDMA_1_DEVICE_ID
#define XPAR_XZDMA_9_BASEADDR 0xFD510000
#define XPAR_XZDMA_9_DMA_MODE 0
#define XPAR_XZDMA_9_HIGHADDR 0xFD51FFFF
#define XPAR_XZDMA_9_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_2 */
#define XPAR_XZDMA_10_DEVICE_ID XPAR_PSU_GDMA_2_DEVICE_ID
#define XPAR_XZDMA_10_BASEADDR 0xFD520000
#define XPAR_XZDMA_10_DMA_MODE 0
#define XPAR_XZDMA_10_HIGHADDR 0xFD52FFFF
#define XPAR_XZDMA_10_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_3 */
#define XPAR_XZDMA_11_DEVICE_ID XPAR_PSU_GDMA_3_DEVICE_ID
#define XPAR_XZDMA_11_BASEADDR 0xFD530000
#define XPAR_XZDMA_11_DMA_MODE 0
#define XPAR_XZDMA_11_HIGHADDR 0xFD53FFFF
#define XPAR_XZDMA_11_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_4 */
#define XPAR_XZDMA_12_DEVICE_ID XPAR_PSU_GDMA_4_DEVICE_ID
#define XPAR_XZDMA_12_BASEADDR 0xFD540000
#define XPAR_XZDMA_12_DMA_MODE 0
#define XPAR_XZDMA_12_HIGHADDR 0xFD54FFFF
#define XPAR_XZDMA_12_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_5 */
#define XPAR_XZDMA_13_DEVICE_ID XPAR_PSU_GDMA_5_DEVICE_ID
#define XPAR_XZDMA_13_BASEADDR 0xFD550000
#define XPAR_XZDMA_13_DMA_MODE 0
#define XPAR_XZDMA_13_HIGHADDR 0xFD55FFFF
#define XPAR_XZDMA_13_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_6 */
#define XPAR_XZDMA_14_DEVICE_ID XPAR_PSU_GDMA_6_DEVICE_ID
#define XPAR_XZDMA_14_BASEADDR 0xFD560000
#define XPAR_XZDMA_14_DMA_MODE 0
#define XPAR_XZDMA_14_HIGHADDR 0xFD56FFFF
#define XPAR_XZDMA_14_ZDMA_CLK_FREQ_HZ 0

/* Canonical definitions for peripheral PSU_GDMA_7 */
#define XPAR_XZDMA_15_DEVICE_ID XPAR_PSU_GDMA_7_DEVICE_ID
#define XPAR_XZDMA_15_BASEADDR 0xFD570000
#define XPAR_XZDMA_15_DMA_MODE 0
#define XPAR_XZDMA_15_HIGHADDR 0xFD57FFFF
#define XPAR_XZDMA_15_ZDMA_CLK_FREQ_HZ 0


/******************************************************************/

#define XPAR_XILPM_ENABLED
#endif  /* end of protection macro */
''')


# Build --------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on KV260")
    parser.add_argument("--build",        action="store_true", help="Build bitstream.")
    parser.add_argument("--load",         action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq", default=100e6,       help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    parser.set_defaults(cpu_type="zynqmp")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.cpu_type == "zynqmp":
        soc.builder = builder
        builder.add_software_package('libxil')
        builder.add_software_library('libxil')
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))


if __name__ == "__main__":
    main()
