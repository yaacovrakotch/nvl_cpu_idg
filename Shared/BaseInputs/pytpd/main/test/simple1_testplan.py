from mod.plans import Plan, ModuleName, QueryTid, qbox, SetProdStep
from setenv_unittest import UT_DIR_REPO
qbox.root = f'{UT_DIR_REPO}/qbox'    # unittest only
SetProdStep('ut05', 'a0')

ModuleName('ARR')
Plan(name='C*A', voltage_corner='nom', content_expect=10, edc=True)
Plan(name='Z*B', voltage_corner='max', content_expect=10)       # waived, not found in TP
Plan(name='C*A', voltage_corner='nom', content_expect=10, module='SCN', tid_expect=QueryTid(attributes='west'))

Plan(name='*D', voltage_corner='nom', content_expect=10, module='SCN')    # not found in TP
Plan(name='C*B', TestMode='{F1_STR}/{UNITTEST_V1}', content_expect=1, module='SCN')       # waived, not found in TP

F1_STR = "1.2"
F1_INT = 12
F1_FLT = 1.2
