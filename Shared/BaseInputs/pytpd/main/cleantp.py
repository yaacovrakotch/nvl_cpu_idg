#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
CleanTP standalone. Run on TP to clean unused instances, plists, TCGs, or all three.

    Usage:   cleantp.py -env <env file, required> <debug, optional>
    example: cleantp.py -env POR_TP/TGLH81/EnvironmentFile.env                # Run default - clean instances, plists, and TCG
             cleantp.py -env POR_TP/TGLH81/EnvironmentFile.env -instance      # Optional -instance flag, only clean instances
             cleantp.py -env POR_TP/TGLH81/EnvironmentFile.env -plist         # Optional -plist flag, only clean plists
             cleantp.py -env POR_TP/TGLH81/EnvironmentFile.env -tcg           # Optional -tcg flag, only clean tcgs
             cleantp.py -env POR_TP/TGLH81/EnvironmentFile.env -revert_tcg    # For testing, will revert .tcg.orig back to .tcg
"""
from setenv import ROOT_ENV      # must be first in the imports
from mod.cleantp_mod import CleanInstance, CleanPlist, CleanTCG, CleanTP, CleanPPR
from tp.testprogram import TestProgram
from gadget.vepargs import Args, TA_StoreTrue, TA_StoreFile
from gadget.dictmore import DictDot
from gadget.helperclass import OPT, CaptureStdoutLog


class CleanTPArgs(Args):
    """
    Defines arguments for script.
    """

    def config(self):
        """
        Define arguments to run CleanTP
        """
        cfg = DictDot()
        cfg.env = TA_StoreFile('Path to ENV File, REQUIRED')
        cfg.instance = TA_StoreTrue('Only Clean Instances, optional')
        cfg.plist = TA_StoreTrue('Only Clean Plists, optional')
        cfg.tcg = TA_StoreTrue('Only Clean TCG, optional')
        cfg.revert = TA_StoreTrue('Revert TCGs, MTPLs, ENV back to original')

        return cfg

    def main(self):
        if OPT.env is None:
            self.print_help()
        tpobj = TestProgram(OPT.env, allpats=True).init()
        is_individual = False
        if OPT.instance:
            cleaninst = CleanInstance(tpobj)
            cleaninst.main()
            is_individual = True

        if OPT.plist:
            cplist = CleanPlist(tpobj)
            cplist.main()
            CleanPPR(tpobj).main()
            is_individual = True

        if OPT.tcg:
            ctcg = CleanTCG(tpobj)
            ctcg.main()
            is_individual = True

        if OPT.revert:
            rev = CleanTP(tpobj)
            rev.revert(tpobj)
            is_individual = True

        if not is_individual:
            clean = CleanTP(tpobj)
            clean.main()


if __name__ == '__main__':  # pragma: no cover
    CleanTPArgs(desc=__doc__).main()
