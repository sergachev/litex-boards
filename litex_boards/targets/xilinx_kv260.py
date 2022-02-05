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

#         libxil_path = os.path.join(self.builder.software_dir, 'libxil')
#         os.makedirs(os.path.realpath(libxil_path), exist_ok=True)
#         lib = os.path.join(libxil_path, 'embeddedsw')
#         if not os.path.exists(lib):
#             os.system("git clone --depth 1 https://github.com/Xilinx/embeddedsw {}".format(lib))
#
#         os.makedirs(os.path.realpath(self.builder.include_dir), exist_ok=True)
#         for header in [
#             'XilinxProcessorIPLib/drivers/uartps/src/xuartps_hw.h',
#             'lib/bsp/standalone/src/common/xil_types.h',
#             'lib/bsp/standalone/src/common/xil_assert.h',
#             'lib/bsp/standalone/src/common/xil_io.h',
#             'lib/bsp/standalone/src/common/xil_printf.h',
#             'lib/bsp/standalone/src/common/xstatus.h',
#             'lib/bsp/standalone/src/common/xdebug.h',
#             'lib/bsp/standalone/src/arm/cortexa9/xpseudo_asm.h',
#             'lib/bsp/standalone/src/arm/cortexa9/xreg_cortexa9.h',
#             'lib/bsp/standalone/src/arm/cortexa9/xil_cache.h',
#             'lib/bsp/standalone/src/arm/cortexa9/xparameters_ps.h',
#             'lib/bsp/standalone/src/arm/cortexa9/xil_errata.h',
#             'lib/bsp/standalone/src/arm/cortexa9/xtime_l.h',
#             'lib/bsp/standalone/src/arm/common/xil_exception.h',
#             'lib/bsp/standalone/src/arm/common/gcc/xpseudo_asm_gcc.h',
#         ]:
#             shutil.copy(os.path.join(lib, header), self.builder.include_dir)
#         write_to_file(os.path.join(self.builder.include_dir, 'bspconfig.h'),
#                       '#define FPU_HARD_FLOAT_ABI_ENABLED 1')
#         write_to_file(os.path.join(self.builder.include_dir, 'xparameters.h'), '''
# #ifndef __XPARAMETERS_H
# #define __XPARAMETERS_H
#
# #include "xparameters_ps.h"
#
# #define STDOUT_BASEADDRESS 0xE0001000
# #define XPAR_PS7_DDR_0_S_AXI_BASEADDR 0x00100000
# #define XPAR_PS7_DDR_0_S_AXI_HIGHADDR 0x3FFFFFFF
#
# #endif
# ''')


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
        # builder.add_software_package('libxil')
        # builder.add_software_library('libxil')
    builder.build(**vivado_build_argdict(args), run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))


if __name__ == "__main__":
    main()
