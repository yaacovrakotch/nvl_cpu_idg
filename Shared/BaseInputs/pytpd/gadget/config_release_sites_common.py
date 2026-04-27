#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u

# Site-specific destination site host and access machines
from .dictmore import TVPVConfigDict

sitecfg_common = TVPVConfigDict()

# =============================================================================
# Site-specific gateway machine list (Sort sites can only be accessed through certain gateway machines)
# These machines have been tested for: D1C, AFO, S24, S28
#
# Each site is allowed two gateway machines to get through the Sort Firewall.  To update the machines,
# you have to submit an LTD ticket.  Please request to have both LTD (D1C,AFO) and VF (S24,S28) Sort sites updated.
#    https://snow.rf3prod.mfg.intel.com/
#
#    Firewall Requests -> Create New
#    Search for "Sort pattern transfer" -> Next
#    Add A Rule
#    Source: <gateway machine>, Destination: <Sort machine>, Services: <leave blank>,
#      Business Justification: <e.g. Updating JF firewall machines for pattern transfer, for both LTD
#      and VF (global)>
#    Click Next
#    In the Description box, add details about the request (e.g. Add these machines to both LTD and VF rules: <list of machines>)
#      and any more information that will help them to process.  For any older machines, indicate that they should not be removed
#      from the firewall until the new machines are configured and tested.  See below for how to test.
#    Scroll down and click the "Submit" button to finalize request
#
#    Test configured firewall machines as p6vector after updating the machines below and sourcing your sandbox:
#      ci_plist.py -testsync all | tee log
#      grep FAILED log
#
# These tickets are assigned to Chen, Llei, so contact her if you need to prioritize a ticket.
# =============================================================================
#
# EC Unix Sites: https://intelpedia.intel.com/EC_Unix_Sites
#
# List of Intel Fabs: https://intelpedia.intel.com/List_of_Intel_Fabs
#
# =============================================================================

access = TVPVConfigDict()
access.AN = 'anlsvmvp03.an.intel.com anls1474.an.intel.com anls1452.an.intel.com'.split()  # anlsvmvp02 is a virtual machine # anlsvlogin01.an.intel.com anlsvlogin02.an.intel.com
access.CH = 'chlr14140.ch.intel.com'.split()
access.FM = 'fmylx9015.fm.intel.com fmci62407.fm.intel.com '.split()  # fmylx9015 is a virtual machine
access.IDC = 'iapp215.iil.intel.com iapp116.iil.intel.com iapp266.iil.intel.com'.split()  # iapp215 is a virtual machine
access.JF = 'plxv9021.pdx.intel.com'.split()  # plxv9021 is a virtual machine
access.PG = 'pglapp02.png.intel.com pgltpl16.png.intel.com pglvmvp002.png.intel.com'.split()  # pglvmvp002 is a virtual machine
access.SC = 'scymve021.sc.intel.com scyapp25.sc.intel.com scyapp26.sc.intel.com'.split()  # scymve021 is a virtual machine # scymve016.sc.intel.com is no longer used
# access.SC1  = 'scycron44.sc.intel.com scydart15.sc.intel.com'.split()
# access.SC3 = 'scy0093.zsc3.intel.com scy0094.zsc3.intel.com'.split()
# access.SC10 = 'scy0047.zsc10.intel.com scy0048.zsc10.intel.com scy0057.zsc10.intel.com'.split()
# access.SC11 = 'scycron81.zsc11.intel.com scycron84.zsc11.intel.com'.split()

# 8/7/17 - kwchen1: this is not used anywhere, and cannot connect to any of the Sort machines
#access.HD  = 'fedhci8001.fedh.intel.com'.split()

# =============================================================================
# SiteCfg common configs
# =============================================================================
# Site: Austin, Texas
sitecfg_common.AN.hosts = 'anls1474.an.intel.com anls1452.an.intel.com'.split()  # anlx6057.an.intel.com anlx5393.an.intel.com
sitecfg_common.AN.access = ''.split()
sitecfg_common.AN.limit = 90

# Site: Chandler, Arizona
sitecfg_common.CH.hosts = 'chlsrsync06.ch.intel.com chlsrsync07.ch.intel.com'.split()
sitecfg_common.CH.access = ''.split()
sitecfg_common.CH.limit = 90

# Site: Folsom, California
# fmylx9013.fm.intel.com use by lab debug
sitecfg_common.FM.hosts = 'fmylx9014.fm.intel.com fmylx9012.fm.intel.com'.split()
sitecfg_common.FM.access = ''.split()
sitecfg_common.FM.limit = 85

# Site: Haifa, Israel
sitecfg_common.IDC.hosts = 'iapp266.iil.intel.com iapp116.iil.intel.com rsync.iil.intel.com'.split()
sitecfg_common.IDC.access = ''.split()
sitecfg_common.IDC.limit = 90

# Site: Jones Farm, Oregon
# plxcrw064.pdx.intel.com plxcrx064.pdx.intel.com # temp remove from config 31 Jan 2021
sitecfg_common.JF.hosts = 'plxv9021.pdx.intel.com plxs1577.pdx.intel.com plxs1578.pdx.intel.com'.split()  # plxv9021.pdx.intel.com plxv9012.pdx.intel.com plxcrw063.pdx.intel.com'.split()  # plxv9021 is also being used for TPTorrent transfers and as backup webserver for them if SC server is down
sitecfg_common.JF.access = ''.split()
sitecfg_common.JF.limit = 85

# Site: Penang, Malaysia
sitecfg_common.PG.hosts = 'pglapp02.png.intel.com pgltpl15.png.intel.com'.split()
sitecfg_common.PG.access = ''.split()
sitecfg_common.PG.limit = 90

# Site: Santa Clara, California
sitecfg_common.SC.hosts = 'scymve021.sc.intel.com scyapp25.sc.intel.com scyapp26.sc.intel.com'.split()
sitecfg_common.SC.access = ''.split()
sitecfg_common.SC.limit = 90

# Site: Santa Clara1 Zone, California
sitecfg_common.SC1.hosts = 'scycron44.sc.intel.com scydart15.sc.intel.com'.split()
sitecfg_common.SC1.access = ''.split()
sitecfg_common.SC1.limit = 90

# Site: Santa Clara1 Zone, California
sitecfg_common.SC3.hosts = 'scy0558.zsc3.intel.com'.split()  # scy0093.zsc3.intel.com scy0094.zsc3.intel.com remove these machine due to /tmp < 10GB
sitecfg_common.SC3.access = ''.split()
sitecfg_common.SC3.limit = 90

# Site: Santa Clara6 Zone, California, PVC
sitecfg_common.SC6.hosts = 'scymve025.sc.intel.com'.split()
sitecfg_common.SC6.access = ''.split()
sitecfg_common.SC6.limit = 90

# Site: Santa Clara7 Zone, California # for PSG
sitecfg_common.SC7.hosts = 'scycron115.zsc7.intel.com'.split()
sitecfg_common.SC7.access = ''.split()
sitecfg_common.SC7.limit = 90

# Site: Santa Clara8 Zone, California # for Alan Jitbit: http://htd_tvpv_help.intel.com/Ticket/52793
sitecfg_common.SC8.hosts = 'scc927018.sc.intel.com'.split()
sitecfg_common.SC8.access = ''.split()
sitecfg_common.SC8.limit = 90

# Site: Santa Clara10 Zone, California
sitecfg_common.SC10.hosts = 'scy0047.zsc10.intel.com scy0048.zsc10.intel.com scy0057.zsc10.intel.com'.split()
sitecfg_common.SC10.access = ''.split()
sitecfg_common.SC10.limit = 90

# Site: Santa Clara11 Zone, California
sitecfg_common.SC11.hosts = 'scycron81.zsc11.intel.com scycron84.zsc11.intel.com'.split()
sitecfg_common.SC11.access = ''.split()
sitecfg_common.SC11.limit = 90

# Site: Santa Clara12 Zone, California
sitecfg_common.SC12.hosts = 'scy0837.zsc12.intel.com scy0838.zsc12.intel.com'.split()
sitecfg_common.SC12.access = ''.split()
sitecfg_common.SC12.limit = 90

# Site: Santa Clara14 Zone, California
sitecfg_common.SC14.hosts = 'scytvpv001.zsc14.intel.com rsync.zsc14.intel.com'.split()
sitecfg_common.SC14.access = ''.split()
sitecfg_common.SC14.limit = 90

# Site: Santa Clara15 Zone, California
sitecfg_common.SC15.hosts = 'scytvpv004.zsc15.intel.com rsync.zsc15.intel.com'.split()
sitecfg_common.SC15.access = ''.split()
sitecfg_common.SC15.limit = 90

# Site: Costa Rica
sitecfg_common.CR.hosts = 'crsrsync001.cr.intel.com crsrsync002.cr.intel.com'.split()
sitecfg_common.CR.access = ''.split()
sitecfg_common.CR.limit = 85

# Site: Assembly Test Development (older division that merged into STTD) Chandler, Arizona
sitecfg_common.ATD.hosts = 'attdeng1.ch.intel.com'.split()
sitecfg_common.ATD.access = ''.split()
sitecfg_common.ATD.limit = 90

# ODS (site is at AL but is counted as a third Die Sort facility)
# Site: Aloha, Oregon
sitecfg_common.ODS.hosts = 'sopsvfr01.al.intel.com sopsvfr02.al.intel.com'.split()
sitecfg_common.ODS.access = ''.split()
sitecfg_common.ODS.limit = 90
sitecfg_common.ODS.pipes = " '/usr/intel/bin/pipes --pipes-path=/home/p6vector/bin/pipes' --chmod=u+rwx,g+rws,o-rwx"  # override default rsh/pipes in shell.py

# Site: Aloha Die Sort, Oregon
sitecfg_common.RA4.hosts = 'al4vprtptxap1.ra.intel.com al4vprtptxap2.ra.intel.com'.split()
sitecfg_common.RA4.access = ''.split()
sitecfg_common.RA4.limit = 90
sitecfg_common.RA4.pipes = " '/usr/intel/bin/pipes --pipes-path=/home/p6vector/bin/pipes' --chmod=u+rwx,g+rws,o-rwx"  # override default rsh/pipes in shell.py

# HOP (HOP is HDMT on Prober verses HDMT on Die (SDx))
# Site: Aloha, Oregon
sitecfg_common.HOP.hosts = 'hopvfr01.al.intel.com'.split()  # hopvfr02.al.intel.com is not ready for use yet
sitecfg_common.HOP.access = ''.split()
sitecfg_common.HOP.limit = 85
sitecfg_common.HOP.pipes = " '/usr/intel/bin/pipes --pipes-path=/home/p6vector/bin/pipes' --chmod=u+rwx,g+rws,o-rwx"  # override default rsh/pipes in shell.py

# SDX (SDx is HDMT on Die)
# Site: Aloha, Oregon
sitecfg_common.SDX.hosts = 'alxpsvfr02.al.intel.com alxpsvfr01.al.intel.com'.split()
sitecfg_common.SDX.access = ''.split()
sitecfg_common.SDX.limit = 94
sitecfg_common.SDX.pipes = " '/usr/intel/bin/pipes --pipes-path=/home/p6vector/bin/pipes' --chmod=u+rwx,g+rws,o-rwx"  # override default rsh/pipes in shell.py

# AFO should be for CMT only, if HDMT2 is requested then they mean AL (different terminology between Sort and TVPV)
# Site: Fab/Sort Aloha, Oregon
sitecfg_common.AFO.hosts = 'afspxfr01.afoprod.mfg.intel.com afspxfr02.afoprod.mfg.intel.com'.split()
sitecfg_common.AFO.access = ''.split()
sitecfg_common.AFO.limit = 85

# AL is same as SDX except legacy TVPV name (before all the different SDx flavors above), is AFO for HDMT2 (AFO STTD Die Sort)
# Site: Aloha, Oregon
sitecfg_common.AL.SAME_AS(sitecfg_common.SDX)

# Site: Fab/Sort 46 Chengdu, China
sitecfg_common.S46.hosts = 's46svxfr01.cd.intel.com s46svxfr02.cd.intel.com'.split()
sitecfg_common.S46.access = ''.split()
sitecfg_common.S46.limit = 90
sitecfg_common.S46.pipes = " '/usr/intel/bin/pipes --pipes-path=/nfs/home/p6vector/bin/pipes' --chmod=u+rwx,g+rws,o-rwx"  # override default rsh/pipes in shell.py

# 8/7/17 - kwchen1: this is not used anywhere, and cannot connect to any of the Sort machines
# Site: Hudson, Massachusetts
#sitecfg_common.HD.hosts     = 'fedhweb01.fedh.intel.com '.split()
# Site: Hudson
sitecfg_common.HD.hosts = 'hdmgrmfg01.hd.intel.com rsync.hd.intel.com'.split()
sitecfg_common.HD.access = ''.split()
sitecfg_common.HD.limit = 90

# Site: Leixlip, Ireland
sitecfg_common.IR.hosts = 'irvrsync001.ir.intel.com irvrsync002.ir.intel.com'.split()
sitecfg_common.IR.access = ''.split()
sitecfg_common.IR.limit = 90

# Site: Bangalore, India
# inesxinf158.iind.intel.com inesxinf160.iind.intel.com# remove for now
sitecfg_common.BA.hosts = 'inlvm01.iind.intel.com inlvm05.iind.intel.com inlc1479.iind.intel.com inlc1484.iind.intel.com inlc1485.iind.intel.com'.split()
sitecfg_common.BA.access = ''.split()
sitecfg_common.BA.limit = 90

# Site: Fort Collins, Colorado
sitecfg_common.FC.hosts = 'fctvpv02.fc.intel.com'.split()
sitecfg_common.FC.access = ''.split()
sitecfg_common.FC.limit = 90

# -----------------------------------------------------------------
# ATM sites - normally TPTorrent should sync this content and not TVPV, except now STTD is doing
# engineering at these sites and TPTorrent will not sync unlocked patches.  For HVM releases,
# product teams are still expected to use TPTorrent.
# -----------------------------------------------------------------
# Site: Penang ATM
sitecfg_common.PGAT.hosts = 'pgsvunix101.png.intel.com pgsvunix102.png.intel.com'.split()
sitecfg_common.PGAT.access = ''.split()
sitecfg_common.PGAT.limit = 90

# Site: Kulim ATM
sitecfg_common.KUAT.hosts = 'kmsvunix101.kssm.intel.com kmsvunix102.kssm.intel.com'.split()
sitecfg_common.KUAT.access = ''.split()
sitecfg_common.KUAT.limit = 90

# Site: Chengdu ATM
sitecfg_common.CDAT.hosts = 'cdsvunix101.cd.intel.com cdsvunix102.cd.intel.com'.split()
sitecfg_common.CDAT.access = ''.split()
sitecfg_common.CDAT.limit = 90
