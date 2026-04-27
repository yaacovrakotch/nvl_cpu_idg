from decimal import ROUND_05UP
import re
from pymtpl.por_methods import PrimeApplyTestConditionTestMethod, PrimePatConfigTestMethod, AuxiliaryTC, PrimeFunctionalTestMethod, PowerSequenceHandler, PrimeDcTestMethod, PrimeSampleRateTestMethod, IVCurve
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeNVLClass, Import, Spec

MODULE_NAME = 'TPI_SHOPS_XKPKGDT'

InitializeNVLClass(f'./{MODULE_NAME}', f'{MODULE_NAME}', 
            defaultrm2bin = (99150000, 99151999), 
            defaultrm1bin = (98150000, 98151999))
 

Import(f'{MODULE_NAME}.usrv')
Import('LevelsSequences_SHOPS.lvl')
Import('BaseLevels_SHOPS.tcg')


##########################################
######### Bin Definitions ################
##########################################
UPPER_OVERFLOW_BIN =    1042
UPPER_SHORTS_BIN =      1062 
UPPER_OPENS_BIN =       1562

LOWER_OVERFLOW_BIN =    1052
LOWER_SHORTS_BIN =      1072
LOWER_OPENS_BIN =       1572

RELAY_FAIL_BIN =        1515
PWRDN_FAIL_BIN =        1517
BRANCH_FAIL_BIN =       1548
SAMPLE_FAIL_BIN =       1550
                              
HW_ALARM_BIN =          9915
SW_ALARM_BIN =          9815

##########################################
######### Flow Returns Definitions #######
##########################################
FAIL_RET =  0
PASS_RET =  1

NUM_TMUX = 8  # Number of TMUX configurations

##########################################
######### DC TEST INSTANCE ###############
##########################################

# Exit Port	Condition	Description
# 0     	Fail	    Fail condition, failing more than one pin or number of pins overflow(more than 28).
# 1	        Pass	    Passing condition.
# 3-99	    Fail	    Fail single rail. Failing port is (PinIndex * 2 + 3) for low limit, (PinIndex * 2 + 4) for high limit.

def get_upper_diode_test(flow, options={'Description':      '', 
                                        'DatalogLevel':     'ALL', 
                                        'Levels':           f'{MODULE_NAME}::all_shops_upper_univ_x_x_pkg_level_cat0', 
                                        'HighLimits':       f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.UPPER_HILIMIT_LOOSE, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.UPPER_HILIMIT_CHOT, {MODULE_NAME}.UPPER_HILIMIT_PHMHOT, {MODULE_NAME}.UPPER_HILIMIT_CCOLD, {MODULE_NAME}.UPPER_HILIMIT_PHMCOLD, {MODULE_NAME}.UPPER_HILIMIT_LOOSE, {MODULE_NAME}.UPPER_HILIMIT_LOOSE))', 
                                        'LowLimits':        f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.UPPER_LOLIMIT_LOOSE, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.UPPER_LOLIMIT_CHOT, {MODULE_NAME}.UPPER_LOLIMIT_PHMHOT, {MODULE_NAME}.UPPER_LOLIMIT_CCOLD, {MODULE_NAME}.UPPER_LOLIMIT_PHMCOLD, {MODULE_NAME}.UPPER_LOLIMIT_LOOSE, {MODULE_NAME}.UPPER_LOLIMIT_LOOSE))', 
                                        'Pins':             f'{MODULE_NAME}.UPPER_PINS',
                                        'BypassPort':       f'{MODULE_NAME}_Rules.If_HVM_TIU(1,-1)',
                                        'Preinstance':      f'',
                                        'Postinstance':     f''
                                        }):

    return IVCurve(name = f'SHOPS_X_SHOPSDC_K_{flow}_X_X_X_X_PKGUPPERDIODE{options["Description"]}',
        LevelsTc = options['Levels'],
        DatalogLevel = options['DatalogLevel'],
		HighLimits = Spec(options['HighLimits']),
		LowLimits = Spec(options['LowLimits']),
        Mode = 'Levels',
        Pins = Spec(options['Pins']),
        SamplingCount = '1',
		Type = 'Voltage',
        BypassPort = Spec(options['BypassPort']),
        PreInstance = options['Preinstance'],
        PostInstance = options['Postinstance'],
        _fitem = Fitem('SAME',
					r0 = pFail(setbin=UPPER_OVERFLOW_BIN, ret = FAIL_RET),
                    r3 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r4 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r5 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r6 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r7 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r8 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r9 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r10 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r11 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r12 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r13 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r14 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r15 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r16 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r17 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r18 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r19 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r20 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r21 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r22 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r23 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r24 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r25 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r26 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r27 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r28 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r29 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r30 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r31 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r32 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r33 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r34 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r35 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r36 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r37 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r38 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r39 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r40 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r41 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r42 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r43 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r44 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r45 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r46 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r47 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r48 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r49 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r50 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r51 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r52 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r53 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r54 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r55 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r56 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r57 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r58 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r59 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r60 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r61 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r62 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r63 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r64 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r65 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r66 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r67 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r68 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r69 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r70 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r71 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r72 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r73 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r74 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r75 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r76 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r77 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r78 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r79 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r80 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r81 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r82 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r83 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r84 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r85 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r86 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r87 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r88 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r89 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r90 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r91 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r92 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r93 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r94 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r95 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r96 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r97 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r98 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET),
                    r99 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r100 = pFail(setbin=UPPER_SHORTS_BIN, ret = FAIL_RET),
                    r101 = pFail(setbin=UPPER_OPENS_BIN, ret = FAIL_RET)
                    ))

def get_lower_diode_test(flow, options={'Description':      '', 
                                        'DatalogLevel':     'ALL', 
                                        'Levels':           f'{MODULE_NAME}::all_shops_lower_univ_x_x_pkg_level_cat0', 
                                        'HighLimits':       f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.LOWER_HILIMIT_LOOSE, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.LOWER_HILIMIT_CHOT, {MODULE_NAME}.LOWER_HILIMIT_PHMHOT, {MODULE_NAME}.LOWER_HILIMIT_CCOLD, {MODULE_NAME}.LOWER_HILIMIT_PHMCOLD, {MODULE_NAME}.LOWER_HILIMIT_LOOSE, {MODULE_NAME}.LOWER_HILIMIT_LOOSE))', 
                                        'LowLimits':        f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.LOWER_LOLIMIT_LOOSE, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.LOWER_LOLIMIT_CHOT, {MODULE_NAME}.LOWER_LOLIMIT_PHMHOT, {MODULE_NAME}.LOWER_LOLIMIT_CCOLD, {MODULE_NAME}.LOWER_LOLIMIT_PHMCOLD, {MODULE_NAME}.LOWER_LOLIMIT_LOOSE, {MODULE_NAME}.LOWER_LOLIMIT_LOOSE))', 
                                        'Pins':             f'{MODULE_NAME}.LOWER_PINS',
                                        'BypassPort':       f'{MODULE_NAME}_Rules.If_HVM_TIU(1,-1)',
                                        'Preinstance':      f'',
                                        'Postinstance':     f''
                                        }):

    return IVCurve(name = f'SHOPS_X_SHOPSDC_K_{flow}_X_X_X_X_PKGLOWERDIODE{options["Description"]}',
        LevelsTc = options['Levels'],
        DatalogLevel = options['DatalogLevel'],
		HighLimits = Spec(options['HighLimits']),
		LowLimits = Spec(options['LowLimits']),
        Mode = 'Levels',
        Pins = Spec(options['Pins']),
        SamplingCount = '1',
		Type = 'Voltage',
        BypassPort = Spec(options['BypassPort']),
        PreInstance = options['Preinstance'],
        PostInstance = options['Postinstance'],
	    _fitem = Fitem('SAME',
				    r0 = pFail(setbin=LOWER_OVERFLOW_BIN, ret = FAIL_RET),
				    r3 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r4 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r5 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r6 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r7 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r8 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r9 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r10 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r11 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r12 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r13 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
					r14 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r15 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r16 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r17 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r18 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r19 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r20 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r21 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r22 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r23 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r24 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r25 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r26 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r27 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r28 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r29 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r30 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r31 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r32 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r33 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r34 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r35 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r36 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r37 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r38 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r39 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r40 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r41 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r42 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r43 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r44 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r45 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r46 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r47 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r48 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r49 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r50 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r51 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r52 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r53 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r54 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r55 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r56 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r57 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r58 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r59 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r60 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r61 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r62 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r63 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r64 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r65 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r66 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r67 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r68 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r69 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r70 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r71 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r72 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r73 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r74 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r75 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r76 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r77 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r78 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r79 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r80 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r81 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r82 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r83 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r84 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r85 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r86 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r87 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r88 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r89 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r90 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r91 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r92 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r93 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r94 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r95 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r96 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r97 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r98 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET),
                    r99 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r100 = pFail(setbin=LOWER_OPENS_BIN, ret = FAIL_RET),
                    r101 = pFail(setbin=LOWER_SHORTS_BIN, ret = FAIL_RET)
                    ))

##########################################
######### DC SHOPS COMPOSITE #############
##########################################
def dc_composite(flow, options={'Description': '', 'DatalogLevel': 'ALL', 'Type': 'HVM'}):
    test_list = []

    # TMUX configuration for all tests
    tmux_config = [
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:0 PCD_TMUXCBIT1:LogicalValue:0 PCD_TMUXCBIT0:LogicalValue:0)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:0 PCD_TMUXCBIT1:LogicalValue:0 PCD_TMUXCBIT0:LogicalValue:1)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:0 PCD_TMUXCBIT1:LogicalValue:1 PCD_TMUXCBIT0:LogicalValue:0)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:0 PCD_TMUXCBIT1:LogicalValue:1 PCD_TMUXCBIT0:LogicalValue:1)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:1 PCD_TMUXCBIT1:LogicalValue:0 PCD_TMUXCBIT0:LogicalValue:0)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:1 PCD_TMUXCBIT1:LogicalValue:0 PCD_TMUXCBIT0:LogicalValue:1)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:1 PCD_TMUXCBIT1:LogicalValue:1 PCD_TMUXCBIT0:LogicalValue:0)",  
        "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:1 PCD_TMUXCBIT1:LogicalValue:1 PCD_TMUXCBIT0:LogicalValue:1)"  
        ]

    if (options['Type'] == 'HVM'):
        # Upper diode test for all 8 TMUX configurations
        for i in range(NUM_TMUX):
            test_options = options.copy()
            levels = f'{MODULE_NAME}::all_shops_upper_univ_x_x_pkg_level_cat0' if (i == 0) else f'{MODULE_NAME}::tmux_config{i}_shops_upper_univ_x_x_pkg_level_cat0'
            test_options.update({
                'Description' : f'_T{i}' + options['Description'], #append additional description
                'Levels': f'{levels}',
                'HighLimits': f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.UPPER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.UPPER_HILIMIT_CHOT_T{i}, {MODULE_NAME}.UPPER_HILIMIT_PHMHOT_T{i}, {MODULE_NAME}.UPPER_HILIMIT_CCOLD_T{i}, {MODULE_NAME}.UPPER_HILIMIT_PHMCOLD_T{i}, {MODULE_NAME}.UPPER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}.UPPER_HILIMIT_LOOSE_T{i}))',
                'LowLimits' : f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.UPPER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.UPPER_LOLIMIT_CHOT_T{i}, {MODULE_NAME}.UPPER_LOLIMIT_PHMHOT_T{i}, {MODULE_NAME}.UPPER_LOLIMIT_CCOLD_T{i}, {MODULE_NAME}.UPPER_LOLIMIT_PHMCOLD_T{i}, {MODULE_NAME}.UPPER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}.UPPER_LOLIMIT_LOOSE_T{i}))', 
                'Pins' : f'{MODULE_NAME}.UPPER_PINS_T{i}',
                'BypassPort' : f'{MODULE_NAME}_Rules.If_HVM_FULL(-1,1,-1)',
                'Preinstance': f'{tmux_config[i]}',
                'Postinstance': f''
                })
        
            test = get_upper_diode_test(flow, test_options)
            test_list.append(test)
            
        # Lower diode test for all 8 TMUX configurations
            test_options = options.copy()
            levels = f'{MODULE_NAME}::all_shops_lower_univ_x_x_pkg_level_cat0' if (i == 0) else f'{MODULE_NAME}::tmux_config{i}_shops_lower_univ_x_x_pkg_level_cat0'
            test_options.update({
                'Description' : f'_T{i}' + options['Description'], #append additional description
                'Levels': f'{levels}',
                'HighLimits': f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.LOWER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.LOWER_HILIMIT_CHOT_T{i}, {MODULE_NAME}.LOWER_HILIMIT_PHMHOT_T{i}, {MODULE_NAME}.LOWER_HILIMIT_CCOLD_T{i}, {MODULE_NAME}.LOWER_HILIMIT_PHMCOLD_T{i}, {MODULE_NAME}.LOWER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}.LOWER_HILIMIT_LOOSE_T{i}))',
                'LowLimits' : f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.LOWER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.LOWER_LOLIMIT_CHOT_T{i}, {MODULE_NAME}.LOWER_LOLIMIT_PHMHOT_T{i}, {MODULE_NAME}.LOWER_LOLIMIT_CCOLD_T{i}, {MODULE_NAME}.LOWER_LOLIMIT_PHMCOLD_T{i}, {MODULE_NAME}.LOWER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}.LOWER_LOLIMIT_LOOSE_T{i}))', 
                'Pins' : f'{MODULE_NAME}.LOWER_PINS_T{i}',
                'BypassPort' : f'{MODULE_NAME}_Rules.If_HVM_FULL(-1,1,-1)',
                'Preinstance': f'',
                'Postinstance': f'{tmux_config[0]}' if (i == NUM_TMUX-1) else '' #reset TMUX configuration after last test
                })
        
            test = get_lower_diode_test(flow, test_options)
            test_list.append(test) 

    elif (options['Type'] == 'FC'):
        # FC with TMUX configuration for all tests
        for i in range(NUM_TMUX):
            # Upper diode test for all 8 TMUX configurations
            test_options = options.copy()
            levels = f'{MODULE_NAME}::all_shops_upper_univ_x_x_pkg_level_cat0' if (i == 0) else f'{MODULE_NAME}::tmux_config{i}_shops_upper_univ_x_x_pkg_level_cat0'
            test_options.update({
                'Description' : f'_T{i}{options["Description"]}',  # T{i} comes before _FC
                'Levels': f'{levels}',
                'HighLimits': f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.FC_UPPER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.FC_UPPER_HILIMIT_CHOT_T{i}, {MODULE_NAME}.FC_UPPER_HILIMIT_PHMHOT_T{i}, {MODULE_NAME}.FC_UPPER_HILIMIT_CCOLD_T{i}, {MODULE_NAME}.FC_UPPER_HILIMIT_PHMCOLD_T{i}, {MODULE_NAME}.FC_UPPER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}.FC_UPPER_HILIMIT_LOOSE_T{i}))',
                'LowLimits' : f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.FC_UPPER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.FC_UPPER_LOLIMIT_CHOT_T{i}, {MODULE_NAME}.FC_UPPER_LOLIMIT_PHMHOT_T{i}, {MODULE_NAME}.FC_UPPER_LOLIMIT_CCOLD_T{i}, {MODULE_NAME}.FC_UPPER_LOLIMIT_PHMCOLD_T{i}, {MODULE_NAME}.FC_UPPER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}.FC_UPPER_LOLIMIT_LOOSE_T{i}))', 
                'Pins' : f'{MODULE_NAME}.FC_UPPER_PINS_T{i}',
                'BypassPort' : f'{MODULE_NAME}_Rules.If_HVM_FULL(1,-1,1)',
                'Preinstance': f'{tmux_config[i]}',
                'Postinstance': f''
                })

            test = get_upper_diode_test(flow, test_options)
            test_list.append(test)
            
            # Lower diode test for all 8 TMUX configurations
            test_options = options.copy()
            levels = f'{MODULE_NAME}::all_shops_lower_univ_x_x_pkg_level_cat0' if (i == 0) else f'{MODULE_NAME}::tmux_config{i}_shops_lower_univ_x_x_pkg_level_cat0'
            test_options.update({
                'Description' : f'_T{i}{options["Description"]}',  # T{i} comes before _FC
                'Levels': f'{levels}',
                'HighLimits': f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.FC_LOWER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.FC_LOWER_HILIMIT_CHOT_T{i}, {MODULE_NAME}.FC_LOWER_HILIMIT_PHMHOT_T{i}, {MODULE_NAME}.FC_LOWER_HILIMIT_CCOLD_T{i}, {MODULE_NAME}.FC_LOWER_HILIMIT_PHMCOLD_T{i}, {MODULE_NAME}.FC_LOWER_HILIMIT_LOOSE_T{i}, {MODULE_NAME}.FC_LOWER_HILIMIT_LOOSE_T{i}))',
                'LowLimits' : f'{MODULE_NAME}_Rules.If_BENCHTOP({MODULE_NAME}.FC_LOWER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}_Rules.If_HOT_PHMHOT_COLD_PHMCOLD_FUSE({MODULE_NAME}.FC_LOWER_LOLIMIT_CHOT_T{i}, {MODULE_NAME}.FC_LOWER_LOLIMIT_PHMHOT_T{i}, {MODULE_NAME}.FC_LOWER_LOLIMIT_CCOLD_T{i}, {MODULE_NAME}.FC_LOWER_LOLIMIT_PHMCOLD_T{i}, {MODULE_NAME}.FC_LOWER_LOLIMIT_LOOSE_T{i}, {MODULE_NAME}.FC_LOWER_LOLIMIT_LOOSE_T{i}))', 
                'Pins' : f'{MODULE_NAME}.FC_LOWER_PINS_T{i}',
                'BypassPort' : f'{MODULE_NAME}_Rules.If_HVM_FULL(1,-1,1)',
                'Preinstance': f'',
                'Postinstance': f'{tmux_config[0]}' if (i == NUM_TMUX-1) else '' #reset TMUX configuration after last test
                })

            test = get_lower_diode_test(flow, test_options)
            test_list.append(test)

    return test_list

    
##########################################
######### FLOW COMPOSITE #################
##########################################    
def shops_flow(flow):
    test_list = []  

    HVM_FC_BRANCH = AuxiliaryTC(name = f'SHOPS_X_AUX_K_{flow}_X_X_X_X_HVM_FC',
        DataType = 'String',
        Datalog = 'Enabled',
        Expression = "[TIU.Type] == 'FULL'",
        ResultPort = '[R]==1?2:1',
        )

    SHOPS_FC = Flow(f'SHOPS_{flow}_FC', dc_composite(flow,{'Description': '_FC', 'DatalogLevel': 'ALL', 'Type': 'FC'}))
    
    ENGID_CQN_BRANCH = AuxiliaryTC(name = f'SHOPS_X_AUX_K_{flow}_X_X_X_X_ENGIDCQNP',
        DataType = 'String',
        Datalog = 'Enabled',
        Expression = "Substring([SCVars.SC_CURRENT_PROCESS_STEP], 0, 3) == 'PHM' || Substring([SCVars.SC_CURRENT_PROCESS_STEP], 0, 3) == 'FUS' || in([SCVars.SC_ENGID],'QQ','QE','QP','QC','QZ','QF','QT')?1:0",
        ResultPort = '[R]==1?2:1',
        )
        
    SAMPLE = PrimeSampleRateTestMethod(name = f'SHOPS_X_SHOPSDC_K_{flow}_X_X_X_X_SAMPLING',
        SamplingRateValue = '20',
        SampleOption = 'DUT_SAMPLING',           
        )
        
    PWRDN_FAIL = PowerSequenceHandler(name = f'SHOPS_X_PWRDWN_K_{flow}_X_X_X_X_FAIL',
        # BypassPort = Spec(1), #REMOVE WHEN LEVELS ARE READY
        ApplyPowerDown = 'Switch',
        PowerDownTc = 'BASE::Power_dwn_PKG_xxx_pwrd_zerzer',
        PreInstance = "SetPinAttributes(--settings=pcd_tmux_all:LogicalValue:0)"        #set TMUX back to default configuraiton
		)

    SHOPS = Flow(f'SHOPS_{flow}', dc_composite(flow))
    if (flow != 'THRFF'):
        SHOPS_NOLOG = Flow(f'SHOPS_{flow}_NOLOG' , dc_composite(flow, {'Description': '_NOLOG', 'DatalogLevel': 'ALL', 'Type': 'HVM'}))              #Set to DatalogLevel=ALL for Poweron, 'DatalogLevel': 'FAIL_ONLY'    #

    # Flow Definition
    if (flow == 'THRFF'):
        return Flow(f'{MODULE_NAME}_{flow}', 
            Fitem('SAME', SHOPS, 
                    r0 = pFail(goto = PWRDN_FAIL.name)),
            Fitem('SAME', PWRDN_FAIL,
                    r0 = pFail(setbin = PWRDN_FAIL_BIN, ret = FAIL_RET),
                    r1 = pPass(ret = FAIL_RET))
            )
                           
    else:
         return Flow(f'{MODULE_NAME}_{flow}',
            Fitem('SAME', HVM_FC_BRANCH,
                    r0 = pFail(setbin = RELAY_FAIL_BIN, ret = FAIL_RET),
                    r1 = pPass(goto = ENGID_CQN_BRANCH.name),
                    r2 = pPass(goto = SHOPS_FC.name)),
            Fitem('SAME', SHOPS_FC,
                    r0 = pFail(goto = PWRDN_FAIL.name),
                    r1 = pPass(ret = PASS_RET)),
            Fitem('SAME', ENGID_CQN_BRANCH,
                    r0 = pFail(setbin = RELAY_FAIL_BIN, ret = FAIL_RET),
                    r1 = pPass(goto = SAMPLE.name),
                    r2 = pPass(goto = SHOPS.name)),
            Fitem('SAME', SAMPLE, 
                    r0 = pFail(setbin = SAMPLE_FAIL_BIN, ret = FAIL_RET),
                    r1 = pPass(goto = SHOPS.name),
                    r2 = pPass(goto = SHOPS_NOLOG.name)),
            Fitem('SAME', SHOPS, 
                    r0 = pFail(goto = PWRDN_FAIL.name),
                    r1 = pPass( ret = PASS_RET)),  
            Fitem('SAME', SHOPS_NOLOG, 
                    r0 = pFail(goto = PWRDN_FAIL.name),
                    r1 = pPass( ret = PASS_RET)),  
            Fitem('SAME', PWRDN_FAIL,
                    r0 = pFail(setbin = PWRDN_FAIL_BIN, ret = FAIL_RET),
                    r1 = pPass(ret = FAIL_RET))
            )
        
##########################################
######### Create Subflows ################
##########################################

START_SUBFLOW = shops_flow('START')