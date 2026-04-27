#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for strmore.py
"""
from setenv_unittest import EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.strmore import *
from gadget.dictmore import DictDot
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, IS_UNIX
from unittest.mock import Mock
from gadget.files import TempDir, File
from io import StringIO
import array
from zlib import compress
from functools import reduce
from os.path import join, exists


class StrTests(unittest.TestCase):

    def test_to_seconds(self):
        self.assertEqual(to_seconds('a'), 0)
        self.assertEqual(to_seconds('11:40:07.018'), 42007.018)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_utc2local(self):
        self.assertEqual(utc2local("2023-05-13T15:40:53Z", is_secs=True), 1683992453)

        # Daylight savings
        self.assertEqual(str(utc2local("2023-05-13T15:40:53Z")), '2023-05-13 08:40:53')
        self.assertEqual(str(utc2local("2023-05-13T15:40:53Z", tzoffset=1)), '2023-05-13 09:40:53')
        # non-Daylight savings
        self.assertEqual(str(utc2local("2023-01-18T01:46:59Z")), '2023-01-17 17:46:59')

    def test_cjoin(self):
        self.assertEqual(cjoin([1, 2, 3]), '1, 2, 3')

    def test_regex_with_not(self):
        self.assertTrue(regex_with_not('bc', 'abcd'))
        self.assertFalse(regex_with_not('!bc', 'abcd'))
        self.assertFalse(regex_with_not('be', 'abcde'))
        self.assertTrue(regex_with_not('!be', 'abcd'))
        with self.assertRaisesRegex(re.error, 'Error on Input Regex'):
            regex_with_not('*', 'abcd')

    def test_wwno(self):
        self.assertEqual(wwno(datetime(2021, 12, 20).timestamp()), 52)  # monday
        self.assertEqual(wwno(datetime(2021, 12, 27).timestamp()), 1)
        self.assertEqual(wwno(datetime(2021, 12, 27).timestamp(), year=True), 202201)
        self.assertEqual(wwno(datetime(2022, 1, 3).timestamp()), 2)
        self.assertEqual(wwno(datetime(2022, 1, 10).timestamp()), 3)
        self.assertEqual(wwno(datetime(2022, 12, 19).timestamp()), 52)
        self.assertEqual(wwno(datetime(2022, 12, 26).timestamp()), 1)
        self.assertEqual(wwno(datetime(2023, 1, 2).timestamp()), 2)
        self.assertEqual(wwno(datetime(2023, 1, 2).timestamp(), year=True), 202302)
        self.assertEqual(wwno(datetime(2024, 1, 8).timestamp(), year=True), 202402)
        self.assertEqual(wwno(datetime(2025, 1, 8).timestamp(), year=True), 202502)
        self.assertEqual(wwno(datetime(2026, 1, 8).timestamp(), year=True), 202602)
        self.assertEqual(wwno(datetime(2027, 1, 8).timestamp(), year=True), 202702)
        self.assertEqual(wwno(datetime(2028, 1, 7).timestamp(), year=True), 202802)
        self.assertGreater(wwno(year=True), 202151)

    def test_putquotes(self):
        self.assertEqual(list(putquotes(['a', 'a b', 'c"d', "c'd", "c'd\"e"])),
                         ['a', "'a b'", "'c\"d'", '"c\'d"', "c'd\"e"])
        self.assertEqual(list(putquotes(['a;b', 'a; b', 'c;"d'])),
                         ["'a;b'", "'a; b'", "'c;\"d'"])

    def test_various_baseN(self):
        self.assertEqual(baseN(2591, 36), "1zz")
        self.assertEqual(baseN(4294967297, 10), "4294967297")
        self.assertEqual(baseN(4347826086956521739, 16), hex(4347826086956521739).replace('0x', ''))
        self.assertEqual(baseN(4347826086956521739, 2), bin(4347826086956521739).replace('0b', ''))
        self.assertEqual(baseN(34, 36), 'y')   # single char
        self.assertEqual(baseN(0, 35), '0')
        self.assertEqual(baseN(1, 35), '1')
        self.assertEqual(baseN(4, 4), '10')    # two char, carry
        self.assertEqual(baseN(5, 4), '11')    # two char, carry plus one

    def test_space2comma(self):
        self.assertEqual(space2comma('abc', 2), 'abc,')
        self.assertEqual(space2comma('abc', 3), 'abc,,')
        self.assertEqual(space2comma('   ', 3), ',,')
        self.assertEqual(space2comma('abc', 1), 'abc')
        self.assertEqual(space2comma(' a,b c ', 3), 'a,b,c')
        self.assertEqual(space2comma('   ab   c d    ', 3), 'ab,c,d')

    def test_sample_list(self):
        self.assertEqual(sample_list(['a', 'b', 'c'], 3), 'a,b,c')    # exact
        self.assertEqual(sample_list(['a', 'b', 'c', 'd'], 3), 'a,b,c,...')    # more
        self.assertEqual(sample_list(['a', 'b'], 3), 'a,b')    # less

    def test_nsplit(self):
        line = "   \t\ta\t\t \t\tbb  \t\t  c d  "
        (x, y) = nsplit(line, 2)
        self.assertEqual(x, "a")
        self.assertEqual(y, "bb c d")
        self.assertEqual(nsplit(line, 1), ["a bb c d"])
        self.assertEqual(nsplit(line, 4), ['a', 'bb', 'c', 'd'])
        self.assertEqual(nsplit(line, 5), ['a', 'bb', 'c', 'd', ''])
        self.assertEqual(nsplit(line, 7), ['a', 'bb', 'c', 'd', ''])

    def test_str_startword(self):
        self.assertEqual(str_startword("   zr(abc)", "zr("), 3)
        self.assertEqual(str_startword("      ,zr(", "zr("), 7)
        self.assertEqual(str_startword("zr(abc)   ", "zr("), 0)
        self.assertEqual(str_startword("zr(abc)   ", "zr(x"), -1)
        self.assertEqual(str_startword("  _zr(abc)", "zr("), -1)

    def test_str_replace(self):
        var = "abcdefghi"
        self.assertEqual(str_replace(var, var.find("cde"), 3, "CDE"), "abCDEfghi")  # normal case
        self.assertEqual(str_replace("abcdef", 2, 1, "Z"), "abZdef")  # Normal case
        self.assertEqual(str_replace("abcdef", 0, 1, "Z"), "Zbcdef")  # Start case
        self.assertEqual(str_replace("abcdef", 5, 1, "Z"), "abcdeZ")  # End of string case
        self.assertEqual(str_replace("abcdef", 3, 2, "ABC"), "abcABCf")  # multi-char
        self.assertEqual(str_replace("abcdef", "abcdef".find("ZZ"), 2, "ABC"), "abcdef")  # not found (-1) case
        self.assertEqual(str_replace("abcdef", 6, 1, "Z"), "abcdefZ")  # maxlength+1 case
        self.assertEqual(str_replace("abcdef", 3, 6, "Z"), "abcZ")  # overlength
        self.assertRaises(Exception, str_replace, "abcdef", 7, 1, "Z")  # out of bounds case

    def test_str_isword(self):
        self.assertEqual(str_isword("abc_123_def"), True)
        self.assertEqual(str_isword("abc_123_def!"), False)
        self.assertEqual(str_isword("abc.123_d.f", "."), True)
        self.assertEqual(str_isword("abc.1-2-3_d.f", "."), False)
        self.assertEqual(str_isword("_.", "."), True)

        # two chars
        self.assertEqual(str_isword("_.a-", ".-"), True)
        self.assertEqual(str_isword("_.a-?", ".-"), False)

        # three chars
        self.assertEqual(str_isword("_.?-?a-", ".-?"), True)
        self.assertEqual(str_isword("_..~a--??", ".-?"), False)

        # reduce syntax
        chr_replace = '.-?'
        newstr = '_..~b--??"'
        self.assertEqual(reduce(lambda s, arg: s.replace(arg, 'a'), chr_replace, newstr),
                         '_aa~baaaa"')

    def test_str_findn(self):
        self.assertEqual(str_findn("aaa", "a", 3), 2)    # basic
        self.assertEqual(str_findn("abc", "a", 2), -1)   # not found on 2nd occurence
        self.assertEqual(str_findn("abcabc", "abc", 2), 3)  # 2nd occurence
        self.assertEqual(str_findn("abcabc", "abc", 1), 0)  # 1st occurence on start
        self.assertEqual(str_findn("abcabc", "def", 1), -1)  # not found on first occurrence

    def test_str_between(self):
        self.assertEqual(str_between("abc [123]", '[', ']'), '123')
        self.assertEqual(str_between("abc '12' a", "'", "'"), '12')
        self.assertEqual(str_between("abc '12' a '23'", "'", "'"), '12')
        self.assertEqual(str_between("'12'", "'", "'"), '12')
        self.assertEqual(str_between("'12'", "a", "'"), None)
        self.assertEqual(str_between("'12'", "'", "a"), None)
        self.assertEqual(str_between("abc '1' a '23'", "'", "'"), '1')
        self.assertEqual(str_between("abc '' a '23'", "'", "'"), '')

        self.assertEqual(str_between("abc_str_ghij", "abc_", "_ghij"), 'str')
        self.assertEqual(str_between("xabc_str_ghij", "abc_", "_ghij"), 'str')
        self.assertEqual(str_between("abstrghij", "ab", "ghij"), 'str')
        self.assertEqual(str_between("xabstrghij", "ab", "ghij"), 'str')
        self.assertEqual(str_between("xabstrghij", "ac", "ghij"), None)
        self.assertEqual(str_between("xabstrghij", "ab", "ghijk"), None)

    def test_multi_replace(self):
        self.assertEqual(multi_replace("ab:d[e]f", ":[]", " "), "ab d e f")
        self.assertEqual(multi_replace("the quick of brown", ["the", "of"], ""), " quick  brown")

    def test_join_make_regex(self):
        self.assertEqual(regex.join_make_regex(["a", "b", "c"]), "[abc]")
        self.assertEqual(regex.join_make_regex(["a", "bb", "c"]), "(a|bb|c)")
        self.assertEqual(regex.join_make_regex(["a", "b", "c"], True), "^[abc]$")
        self.assertEqual(regex.join_make_regex(["a", "b", "c"], True, reverse_sort=True), "^[cba]$")
        self.assertEqual(regex.join_make_regex(["aa"],), "aa")
        self.assertEqual(regex.join_make_regex(["a"],), "a")

    def test_to_non_capture_group(self):
        self.assertEqual(regex.to_non_capture_group('(abc|def)'), '(?:abc|def)')
        self.assertEqual(regex.to_non_capture_group('abc|def'), 'abc|def')

    def test_compare_print(self):
        with MockVar(sys, "stdout", StringIO()) as p:
            compare_print("ABCDE", "ABDDF")
            self.assertEqual(p.getvalue(), ('ABCDE\n'
                                            'ABDDF\n'
                                            '  $ $\n'))
            p.seek(0)
            p.truncate()
            compare_print("ABCEFG", "BBCE")
            self.assertEqual(p.getvalue(), ('ABCEFG\n'
                                            'BBCE\n'
                                            '$   $$\n'))
            p.seek(0)
            p.truncate()
            compare_print("ABCE", "BBCEFG")
            self.assertEqual(p.getvalue(), ('ABCE\n'
                                            'BBCEFG\n'
                                            '$   $$\n'))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_curtime(self):
        self.assertRegex(curtime(), r'20\d\d-\d+-\d+_\d+:\d+:\d+')
        self.assertRegex(curtime(number=True), r'20\d\d{5}_\d{6}_\d+')
        self.assertRegex(curtime(seconds=1409418276), r'2014-08-\d{2}')
        self.assertRegex(curtime(iso=True), r'20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+')
        self.assertRegex(curtime(seconds=1409418276, dateonly=True), r'^2014-08-\d{2}$')
        self.assertEqual(curtime(1409418276, number=True), '20140830_100436_000000')
        self.assertEqual(curtime(1409418276, human=True), '2014-08-30 10:04:36')
        self.assertRaises(AssertionError, curtime, 1409418276, human=True, number=True)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_day_code(self):
        self.assertEqual(day_code(seconds=100), 'cb620')
        self.assertNotEqual(day_code(), 'cb620')
        self.assertEqual(len(day_code()), 5)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_workweek(self):
        self.assertEqual(workweek(date='2019-1-30'), '2019.ww05.3')
        self.assertEqual(workweek(date='2019-10-12'), '2019.ww41.6')
        self.assertEqual(workweek(date='2020-1-6'), '2020.ww02.1')
        self.assertEqual(workweek(1634496981), '2021.ww42.0')      # was ww43.7 in intel_workweek() routine
        self.assertEqual(workweek(secs=1679406334), '2023.ww12.2')

        # specific date - with leading zero
        self.assertEqual(workweek(secs=1676814334), '2023.ww08.0')

        # 2022
        self.assertEqual(workweek(date='2022-06-29'), '2022.ww27.3')

        # today
        self.assertTrue(re.search(r"^\d\d\d\d.ww\d\d\.\d$", workweek()))

    def test_str_index_expander(self):
        self.assertListEqual(str_index_expander("3-0,5,8-10", msb2lsb=True), [10, 9, 8, 5, 3, 2, 1, 0])
        self.assertEqual(str_index_expander("2"), [2])
        self.assertListEqual(str_index_expander(" 2-4, 3-5"), [2, 3, 4, 5])
        self.assertListEqual(str_index_expander("8-6,2-4,  10-12"), [2, 3, 4, 6, 7, 8, 10, 11, 12])
        self.assertListEqual(str_index_expander("8-6,2-4,  10-12", msb2lsb=True), [12, 11, 10, 8, 7, 6, 4, 3, 2])
        self.assertListEqual(str_index_expander("aa-ae"), [100, 101, 102, 103, 104])

    def test_wordgen(self):
        self.assertEqual(''.join(wordgen(1)), "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(len(set(wordgen(1))), 63)
        self.assertEqual(len(set(wordgen(2))), 63 * 63)
        self.assertEqual(len(set(wordgen(3))), 63 * 63 * 63)
        self.assertEqual(list(wordgen(2))[0], '00')
        self.assertEqual(list(wordgen(2))[-1], 'zz')
        self.assertEqual(list(wordgen(2))[-2], 'zy')

    def test_strn(self):
        self.assertIsNone(strvalue(None))
        self.assertEqual(strvalue(0), '0')
        self.assertEqual(strvalue(12), '12')
        self.assertEqual(strvalue('12a'), '12a')

    def test_truncate(self):
        # string
        self.assertEqual(truncate('a\nb\nc\nd'), 'a\nb\nc\nd')
        self.assertEqual(truncate('a\nb\nc\nd', n=2), 'a\nb\n   ... 2 more lines not displayed.')
        # list
        inlist = ['a', 'b\n', 'c', 'd']
        self.assertEqual(truncate(inlist), 'a\nb\nc\nd')
        self.assertEqual(truncate(inlist, n=3), 'a\nb\nc\n   ... 1 more lines not displayed.')
        # empty
        self.assertEqual(truncate(''), '')
        self.assertEqual(truncate([]), '')

        # iterator, with stuff at eol
        def x_iter():
            for item in ['a \n', 'b\n', 'c', 'd\n']:
                yield item

        self.assertEqual(truncate(x_iter()), 'a\nb\nc\nd')
        self.assertEqual(truncate(x_iter(), n=3), 'a\nb\nc\n   ... 1 more lines not displayed.')

    def test_md5(self):
        self.assertEqual(md5(""), "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(md5("somestring"), "1f129c42de5e4f043cbd88ff6360486f")
        self.assertEqual(md5(12.5), "cf3e481a44141cabd4e9d46cfbb1f899")

        # gz object
        aa = compress(("j".zfill(10000)).encode('utf-8'))
        self.assertEqual(len(aa), 35)
        self.assertEqual(len(md5(aa)), 32)

    def test_sha1(self):
        self.assertEqual(sha1(""), "da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(sha1("Somestring"), "ac7e4265446aa47cd4c89b50ecba266831af9fac")
        self.assertEqual(sha1(12.5), "90db4c034fdf9f384fce435b9f9b57de9906c45c")

        # gz object
        aa = compress(("j".zfill(10000)).encode())
        self.assertEqual(len(aa), 35)
        self.assertEqual(len(sha1(aa)), 40)

        # bytes
        self.assertEqual(sha1(b"Somestring"), "ac7e4265446aa47cd4c89b50ecba266831af9fac")

    def test_essm_hash_name(self):
        self.assertEqual(essm_hash_name('page1,page1'), 'E_5c56703f86f715ba')

    def test_uniq_int(self):
        self.assertEqual(uniq_int(""), 982798738632651952)
        self.assertEqual(uniq_int(51), 828300345313605409)  # non string

    def test_indent(self):
        self.assertEqual(indent(0, "abc"), "abc")
        self.assertEqual(indent(0, []), "")
        self.assertEqual(indent(0, ["a"]), "a")
        self.assertEqual(indent(0, ["a", "b"]), "a\nb")
        self.assertEqual(indent(1, ["a"]), " a")
        self.assertEqual(indent(1, ["a", "b"]), " a\n b")
        self.assertEqual(indent(2, ["aa", "bb", "cc"]), "  aa\n  bb\n  cc")
        self.assertEqual(indent(3, "abc\ndef"), "   abc\n   def")
        self.assertEqual(indent(4, "aa\nbb\ncc\ndd"), "    aa\n    bb\n    cc\n    dd")
        self.assertEqual(indent(3, None), '')
        self.assertEqual(indent(3, [None]), '   None')

    def test_str_repeat(self):
        self.assertEqual(str_repeat(3), '   ')
        self.assertEqual(str_repeat(1), ' ')
        self.assertEqual(str_repeat(0), '')
        self.assertEqual(str_repeat(5, 'a'), 'aaaaa')
        self.assertRaisesRegex(ValueError, "can only take", str_repeat, 5, '12')

    def test_split_spacetab(self):
        self.assertEqual(split_spacetab('a  b  c  d\na\tb \t c\t \td\t\n'),
                         ['a b c d',
                          'a b c d ',
                          ''])

    def test_age_string(self):
        self.assertEqual(age_string(2.122), "2 secs")
        self.assertEqual(age_string(125), "2 mins")
        self.assertEqual(age_string(3600 * 3), "3 hours")
        self.assertEqual(age_string(3600 * 24 * 4), "4 days")
        self.assertEqual(age_string(3600 * 24 * 60), "2 months")
        self.assertEqual(age_string(3600 * 24 * 365 * 4), "4 years")

    def test_separate_chars(self):
        self.assertEqual(separate_chars(2, "08080402"), ['08', '08', '04', '02'])  # complete
        self.assertEqual(separate_chars(2, "0808040"), ['08', '08', '04', '0'])  # complete with partial
        self.assertEqual(separate_chars(2, "08"), ['08'])  # one element full
        self.assertEqual(separate_chars(2, "0"), ['0'])  # one element partial
        self.assertEqual(separate_chars(2, ""), [])  # empty
        self.assertEqual(separate_chars(1, "08080402"), list("08080402"))  # len==1
        self.assertEqual(separate_chars(3, "0808040"), ['080', '804', '0'])   # complete with partial
        self.assertEqual(separate_chars(3, "080804004"), ['080', '804', '004'])  # complete

    def test_comma_key_value(self):
        self.assertEqual(comma_key_value({}), "")
        self.assertEqual(comma_key_value({'aa': '12'}), "aa='12'")
        self.assertEqual(comma_key_value({'aa': '12', 'bb': 23}), "aa='12', bb=23")
        self.assertEqual(comma_key_value({'a': '12', 'b': 23, 'c': None}), "a='12', b=23, c=None")

    def test_nospace_comment(self):
        self.assertEqual(list(nospace_comment('\n\n  \nvalid line\n   # comment\nline2\n\n#lineend\n')),
                         ['valid line', 'line2'])
        self.assertEqual(list(nospace_comment(['', '   ', '# comment', 'validline', '', 'line2'])),
                         ['validline', 'line2'])
        self.assertEqual(list(nospace_comment(['## com1', '# com2'], commentchar='##')),
                         ['# com2'])

    def test_subdivide(self):
        self.assertEqual(list(subdivide('1234567', 3)), ['123', '456', '7'])
        self.assertEqual(list(subdivide('12345678', 3)), ['123', '456', '78'])
        self.assertEqual(list(subdivide('123456', 3)), ['123', '456'])
        self.assertEqual(list(subdivide('1234567', 2)), ['12', '34', '56', '7'])
        self.assertEqual(list(subdivide('123456', 2)), ['12', '34', '56'])
        self.assertEqual(list(subdivide('123456', 1)), ['1', '2', '3', '4', '5', '6'])

        # limit has reached
        self.assertEqual(list(subdivide('123456', 2, 2)), ['12', '34'])

    def test_line_word_wrap(self):
        # normal case
        self.assertEqual(list(line_word_wrap('abcd efg 123', 4)), ['abcd', 'efg', '123'])
        self.assertEqual(list(line_word_wrap('abcd      efg     123', 4)), ['abcd', 'efg', '123'])
        self.assertEqual(list(line_word_wrap('a b c d e f g h', 4)), ['a b', 'c d', 'e f', 'g h'])
        self.assertEqual(list(line_word_wrap('a bb c d e f g hh', 4)), ['a bb', 'c d', 'e f', 'g', 'hh'])  # bec ' g hh' is more than 4 chars
        # very long case
        self.assertEqual(list(line_word_wrap('abcdefg 123', 4)), ['abcd', 'efg', '123'])
        # maxlen longer than line
        self.assertEqual(list(line_word_wrap('abcdefg 123', 40)), ['abcdefg 123'])
        # exact match
        self.assertEqual(list(line_word_wrap('abcd efgh', 4)), ['abcd', 'efgh'])
        self.assertEqual(list(line_word_wrap('abcd.efgh', 4)), ['abcd', '.', 'efgh'])
        self.assertEqual(list(line_word_wrap('abcd', 4)), ['abcd'])
        self.assertEqual(list(line_word_wrap('abcdefgh', 4)), ['abcd', 'efgh'])
        self.assertEqual(list(line_word_wrap('abcdefg', 4)), ['abcd', 'efg'])

        # limit exhausted
        self.assertEqual(list(line_word_wrap('a bb c d e f g hh', 4, limit=2)),
                         ['a bb', 'c d', 'e f g hh'])

    def test_is_ascii(self):
        self.assertTrue(is_ascii('abc def'))
        self.assertFalse(is_ascii('abc\xfe def'))
        self.assertEqual(to_ascii('abc \ndef'), 'abc \ndef')
        self.assertEqual(to_ascii('abc\xfedef\xabc'), 'abc def c')

    def test_to_alpha_numeric(self):
        """
        Functional test for to_alpha_numeric, removes non alpha numeric characters from string
        :return:
        """
        # case: string is already alpha numeric, no chars should be removed
        self.assertEqual(to_alpha_numeric('abc123'), 'abc123')

        # case: string contains special characters, should be removed
        self.assertEqual(to_alpha_numeric('ab$cd.123?'), 'abcd123')

        # case: string is only special characters, should return emtpy string
        self.assertEqual(to_alpha_numeric('!@#$%^>..'), '')

        # case: input string is empty, should return emtpy string
        self.assertEqual(to_alpha_numeric(''), '')

    def test_to_str(self):
        v1 = b'somebytes'
        v2 = 'somestr'
        self.assertTrue(isinstance(to_str(v1), str))
        self.assertEqual(to_str(v1), 'somebytes')
        self.assertTrue(isinstance(to_str(v2), str))
        self.assertEqual(to_str(v2), 'somestr')

        self.assertTrue(isinstance(to_bytes(v1), bytes))
        self.assertEqual(to_bytes(v1), b'somebytes')
        self.assertTrue(isinstance(to_bytes(v2), bytes))
        self.assertEqual(to_bytes(v2), b'somestr')

    def test_zlib_compress_uncompress(self):
        self.assertEqual(zlib_uncompress(zlib_compress("Hello")).decode(), "Hello")
        self.assertNotEqual(zlib_compress("Hello"), b"Hello")
        self.assertNotEqual(zlib_compress("Hello"), "Hello")
        self.assertEqual(zlib_uncompress(zlib_compress(b"Hello")).decode(), "Hello")
        with self.assertRaises(ValueError):
            zlib_compress(11)

    def test_dict_to_args(self):
        self.assertEqual(dict_to_args({}), '')
        self.assertEqual(dict_to_args(dict(abc=123)), 'abc=123')
        self.assertEqual(dict_to_args(dict(ghi='txt', abc=123)), "abc=123, ghi='txt'")

    def test_dict2sorted_string(self):
        # Fail Case
        with self.assertRaises(TypeError):
            dict2sorted_string(['a', 'b', 'c'])

        dd = {'a': 1, 'c': 2, 'b': 3}
        # Sort by Key
        self.assertEqual(dict2sorted_string(dd), "{'a': 1, 'b': 3, 'c': 2}")
        # Sort by Value
        self.assertEqual(dict2sorted_string(dd, False), "{'a': 1, 'c': 2, 'b': 3}")

    def test_to_list(self):
        self.assertEqual(to_list([1, 2]), [1, 2])
        self.assertEqual(to_list((1, 2)), (1, 2))
        self.assertEqual(to_list(1), (1, ))
        res = to_list(deque([1]))
        self.assertEqual(res, [1])
        self.assertTrue(isinstance(res, list))

    def test_join_seq(self):
        self.assertEqual(join_seq([]), '\n')
        self.assertEqual(join_seq(['a']), 'a\n')
        self.assertEqual(join_seq(['a', 'b']), 'a\nb\n')
        self.assertEqual(join_seq(['a', 'b', 'c']), 'a\nb\nc\n')
        self.assertEqual(join_seq(['a', 2, 'c']), 'a\n2\nc\n')    # non-string mix

    def test_soc_sha(self):
        with TempDir(name=True) as tdir:
            content = """line1 text1
line2 text1
line3 text1"""
            fname = File(join(tdir, 'a.soc')).touch(content, newfile=True).get_name()
            self.assertEqual(soc_sha(fname), '19808a4c4768')

            # with empty lines
            content = """
line1 text1


line2 text1
line3 text1
"""
            fname = File(join(tdir, 'a.soc')).touch(content, newfile=True).get_name()
            self.assertEqual(soc_sha(fname), '19808a4c4768')

            # with trailing spaces and spaces between 1. The backlash at end is for pep8 ignore
            content = """
    line1 text1

 line2 text1      \
\nline3         text1
"""
            fname = File(join(tdir, 'a.soc')).touch(content, newfile=True).get_name()
            self.assertEqual(soc_sha(fname), '19808a4c4768')

            # with trailing spaces and spaces between 2. The backlash at end is for pep8 ignore
            content = """
    line1    text1

 line2              text1    \
\nline3 text1
"""
            fname = File(join(tdir, 'a.soc')).touch(content, newfile=True).get_name()
            self.assertEqual(soc_sha(fname), '19808a4c4768')

            # with different contents 1
            content = """
line1 text1 # comment

line2 text1
line3 text1
"""
            fname = File(join(tdir, 'a.soc')).touch(content, newfile=True).get_name()
            self.assertEqual(soc_sha(fname), '0879b70f152f')

            # with different contents 2
            content = """
line1 text 1

line2 text1
line3 text1
"""
            fname = File(join(tdir, 'a.soc')).touch(content, newfile=True).get_name()
            self.assertNotEqual(soc_sha(fname), '19808a4c4768')
            self.assertEqual(soc_sha(fname, debug=True).split('\n'), ['line1 text 1',
                                                                      'line2 text1',
                                                                      'line3 text1'])

    def test_to_char_array(self):
        """
        Functional test for to_char_array
        :return:
        """
        str = 'foo'
        self.assertEqual(to_char_array(str), array.array('u', list(str)))   # py3

    def test_to_py3_oct(self):
        """
        Functional test for to_py3_oct
        :return:
        """
        str = '0750'
        self.assertEqual(to_py3_oct(str), '0o750')  # else convert to py3 oct format

    def test_to_bytes_list(self):
        """
        Functional test for to_bytes_list
        :return:
        """
        list = ['foo', 'bar']
        self.assertEqual(to_bytes_list(list), [b'foo', b'bar'])  # converted to bytes in py3

    def test_to_list_of_bytes(self):
        """
        Functional test for to_list_of_bytes (py3 only)
        :return:
        """
        # tests for py3, should turn a str/byte string into a list of bytes characters
        str = 'abcd'
        self.assertEqual(to_list_of_bytes(str), [b'a', b'b', b'c', b'd'])
        str = '1234'
        self.assertEqual(to_list_of_bytes(str), [b'1', b'2', b'3', b'4'])
        str = b'abcd'
        self.assertEqual(to_list_of_bytes(str), [b'a', b'b', b'c', b'd'])
        str = b'1234'
        self.assertEqual(to_list_of_bytes(str), [b'1', b'2', b'3', b'4'])

    def test_dict_to_byte_dict(self):
        """
        Functional test for dict_to_byte_dict
        :return:
        """
        dict = {'str_key': 'str_value',
                'int_key': 2,
                'dict_key': {'dict_key2a': 'dict_val2a', 'dict_key2b': 'dict_val2b'},
                'list_key': ['list1', 'list2'],
                'byte_key': b'22',
                'misc_key': 3.5}

        self.assertEqual(dict_to_byte_dict(dict), {b'str_key': b'str_value',
                                                   b'int_key': 2,
                                                   b'dict_key': {b'dict_key2a': b'dict_val2a', b'dict_key2b': b'dict_val2b'},
                                                   b'list_key': [b'list1', b'list2'],
                                                   b'byte_key': b'22',
                                                   b'misc_key': 3.5})

    def test_uniq_sha(self):
        self.assertNotEqual(uniq_sha(), uniq_sha())
        self.assertEqual(len(uniq_sha()), 40)

    def test_eval_expr(self):
        self.assertEqual(4, eval_expr('2^6'))
        self.assertEqual(64, eval_expr('2**6'))
        self.assertEqual(-5.0, eval_expr('1 + 2*3**(4^5) / (6 + -7)'))
        self.assertEqual(-2, eval_expr('-(2)'))
        self.assertRaises(TypeError, eval_expr, 'A')


class Base776Tests(TestCase):

    def test_encode(self):
        self.assertEqual(Base776.encode(0), "00")
        self.assertEqual(Base776.encode(1), "01")
        self.assertEqual(Base776.encode(11), "11")
        self.assertEqual(Base776.encode(99), "99")
        self.assertEqual(Base776.encode(100), "aa")
        self.assertEqual(Base776.encode(125), "az")
        self.assertEqual(Base776.encode(126), "ba")
        self.assertEqual(Base776.encode(127), "bb")
        self.assertEqual(Base776.encode(255), "fz")
        self.assertEqual(Base776.encode(775), "zz")

        self.assertRaisesRegex(Exception, "Cannot Base776.encode",
                               Base776.encode, 776)
        self.assertRaisesRegex(Exception, "Cannot Base776.encode",
                               Base776.encode, -1)

    def test_decode(self):
        self.assertEqual(Base776.decode("00"), 0)
        self.assertEqual(Base776.decode("01"), 1)
        self.assertEqual(Base776.decode("11"), 11)
        self.assertEqual(Base776.decode("99"), 99)
        self.assertEqual(Base776.decode("aa"), 100)
        self.assertEqual(Base776.decode("az"), 125)
        self.assertEqual(Base776.decode("ba"), 126)
        self.assertEqual(Base776.decode("bb"), 127)
        self.assertEqual(Base776.decode("fz"), 255)

        self.assertRaisesRegex(Exception, "Base776.decode can only take two char",
                               Base776.decode, '0')
        self.assertRaisesRegex(Exception, r"Invalid input \[a0\] to Base776.decode()",
                               Base776.decode, 'a0')

    def test_all_combinations(self):
        # unique chars for all combinations
        result = set()
        for ii in range(776):
            result.add(Base776.encode(ii))
        self.assertEqual(len(result), 776)

        # decode them - must all be unique
        result2 = set()
        for item in result:
            result2.add(Base776.decode(item))
        self.assertEqual(len(result2), 776)


class Base3844Tests(TestCase):

    def test_encode(self):
        #  00->99, aa-zz (100-775), aA-z9 (776 - 1711), Aa-Z9 (1712 - 3323), 0a-9Z (3324 - 3843) mapping

        # Same as Base776 tests
        self.assertEqual(Base3844.encode(0), "00")
        self.assertEqual(Base3844.encode(1), "01")
        self.assertEqual(Base3844.encode(11), "11")
        self.assertEqual(Base3844.encode(99), "99")
        self.assertEqual(Base3844.encode(100), "aa")
        self.assertEqual(Base3844.encode(125), "az")
        self.assertEqual(Base3844.encode(126), "ba")
        self.assertEqual(Base3844.encode(127), "bb")
        self.assertEqual(Base3844.encode(255), "fz")
        self.assertEqual(Base3844.encode(775), "zz")

        # Tests for 776 - 3844
        self.assertEqual(Base3844.encode(776), "aA")
        self.assertEqual(Base3844.encode(801), "aZ")
        self.assertEqual(Base3844.encode(811), "a9")
        self.assertEqual(Base3844.encode(812), "bA")

        self.assertEqual(Base3844.encode(871), "cX")
        self.assertEqual(Base3844.encode(1500), "uE")
        self.assertEqual(Base3844.encode(1711), "z9")

        self.assertEqual(Base3844.encode(1712), "Aa")
        self.assertEqual(Base3844.encode(2500), "MS")
        self.assertEqual(Base3844.encode(3200), "Ya")
        self.assertEqual(Base3844.encode(3323), "Z9")

        self.assertEqual(Base3844.encode(3324), "0a")
        self.assertEqual(Base3844.encode(3500), "3u")
        self.assertEqual(Base3844.encode(3804), "9m")
        self.assertEqual(Base3844.encode(3843), "9Z")

        self.assertRaisesRegex(Exception, "Cannot Base3844.encode", Base3844.encode, 3844)
        self.assertRaisesRegex(Exception, "Cannot Base3844.encode", Base3844.encode, -1)

        self.assertRaisesRegex(Exception, "Base3844 is up to 3843", Base3844._get_offset_encode, 3844)

    def test_decode(self):

        # Test '00'-'99' , 'aa'-'zz'
        self.assertEqual(Base3844.decode("00"), 0)
        self.assertEqual(Base3844.decode("01"), 1)
        self.assertEqual(Base3844.decode("11"), 11)
        self.assertEqual(Base3844.decode("99"), 99)
        self.assertEqual(Base3844.decode("aa"), 100)
        self.assertEqual(Base3844.decode("az"), 125)
        self.assertEqual(Base3844.decode("ba"), 126)
        self.assertEqual(Base3844.decode("bb"), 127)
        self.assertEqual(Base3844.decode("fz"), 255)
        self.assertEqual(Base3844.decode("zz"), 775)

        # Test aA-z9 (776 - 1711), Aa-Z9 (1712 - 3323), 0a-9Z (3324 - 3843) mapping
        self.assertEqual(Base3844.decode("aA"), 776)
        self.assertEqual(Base3844.decode("aZ"), 801)
        self.assertEqual(Base3844.decode("a9"), 811)
        self.assertEqual(Base3844.decode("bA"), 812)

        self.assertEqual(Base3844.decode("cX"), 871)
        self.assertEqual(Base3844.decode("uE"), 1500)
        self.assertEqual(Base3844.decode("z9"), 1711)

        self.assertEqual(Base3844.decode("Aa"), 1712)
        self.assertEqual(Base3844.decode("MS"), 2500)
        self.assertEqual(Base3844.decode("Ya"), 3200)
        self.assertEqual(Base3844.decode("Z9"), 3323)

        self.assertEqual(Base3844.decode("0a"), 3324)
        self.assertEqual(Base3844.decode("3u"), 3500)
        self.assertEqual(Base3844.decode("9m"), 3804)
        self.assertEqual(Base3844.decode("9Z"), 3843)

        self.assertRaisesRegex(Exception, "Base3844.decode() can only take two char", Base3844.decode, '0')
        self.assertRaisesRegex(Exception, r"Invalid input \[a@\] to Base3844.decode()", Base3844.decode, 'a@')

        with MockVar(Base3844, '_char_to_base62_value', Mock(return_value=60)):
            self.assertRaisesRegex(Exception, "Cannot decode", Base3844.decode, 'a5')

    def test_all_combinations(self):

        # unique chars for all combinations
        result = set()
        for ii in range(3844):
            result.add(Base3844.encode(ii))
        self.assertEqual(len(result), 3844)

        # decode them - must all be unique
        result2 = set()
        for item in result:
            result2.add(Base3844.decode(item))
        self.assertEqual(len(result2), 3844)


class RegexTests(TestCase):

    def test_regex(self):
        line = 'The quick brown fox'
        self.assertEqual(bool(regex('quick', line)), True)
        self.assertEqual(bool(regex('Quick', line)), False)
        self.assertEqual(bool(regex('quick', line, pre='quicky')), False)  # 1
        self.assertEqual(bool(regex('quick', line, pre='quick')), True)  # 2
        self.assertEqual(bool(regex('QUIck', line, re.IGNORECASE)), True)  # 3
        self.assertEqual(bool(regex('Quicky', line, re.IGNORECASE)), False)  # 4

        line = 'The Quick brown fox'
        self.assertEqual(bool(regex('quick', line, re.IGNORECASE, pre='Quick')), True)  # 5
        self.assertEqual(bool(regex('quick', line, re.IGNORECASE, pre='quicky')), False)  # 6

    def test_group(self):
        self.assertRaises(AttributeError, group, 1)

        line = "Pat pstate; #123"
        self.assertEqual(bool(regex(r'Pat\s+(\w+);.*#(.*)', line)), True)
        self.assertEqual(group(1), "pstate")
        self.assertEqual(group(2), "123")

    def test_RegexCompile(self):
        robj = RegexCompile()
        line = "The quick brown fox"
        r1 = robj.compile(r'(qu\w+)')
        self.assertEqual(r1.search(line).group(1), "quick")   # this will confirm it is a re object
        r1 = robj.compile(r'(qu\w+)')
        r2 = robj.compilef(r'(qu\w+)  # test', re.X)
        self.assertEqual(r1.search(line).group(1), "quick")   # this will confirm it is a re object
        r2 = robj.compilef(r'(qu\w+)  # test', re.X)
        self.assertEqual(robj.count(), 2)
        self.assertEqual(robj.get_totalcalls(), 4)

    def test_key_compile_regex(self):
        dd = DictDot()
        dd.xml = r'(\w+)\.xml'
        dd.rpt = r'\w+\.rpt'
        regex.key_compile_regex(dd, list(dd.keys()))
        regex.key_compile_regex(dd, list(dd.keys()))
        self.assertEqual(dd.xml_robj.search('abc.xml').group(1), "abc")
        self.assertEqual(len(dd), 4)

    def test_printWithUnits(self):
        # Assert to check printWithUnits method
        self.assertEqual(printWithUnits(745), "745 B")
        self.assertEqual(printWithUnits(331976), "324.2 KB")
        self.assertEqual(printWithUnits(557947289), "532.1 MB")
        self.assertEqual(printWithUnits(130567005798), "121.6 GB")


class HtmlLinkerTests(TestCase):

    def test_link_regex(self):
        """Need to ensure that the complex regex's catch expected usages"""
        linker = HtmlLinker()

        # Test Rally Formats
        t_type = linker.ticket_types.RALLY
        link_regex = linker.linker_types[t_type]['id_regex']
        msg = "US12345 comes first"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'US12345', "Found Rally ID as 1st item")
        msg = "Rally (US12345) in parens"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'US12345', "Found Rally ID in parens")
        msg = "Rally ID is last US12345"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'US12345', "Found Rally ID as last")
        msg = "Not a Rally ID POTUS12345"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE), None, "Rally ID doesn't over grab")

        # Test TVPVHelp Formats
        t_type = linker.ticket_types.TVPVHELP
        link_regex = linker.linker_types[t_type]['id_regex']
        msg = "TVPVHelp 12345 first"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'TVPV 1st')
        msg = "TVPVHelp12345 first"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'TVPV w/o space')
        msg = "TVPVHelp: 12345"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'TVPV w/ :')
        msg = "tvpvhelp: 12345"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'TVPV lowercase :')
        msg = "TVPV Help #12345 and stuff"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'TVPV w/ #')
        msg = "HSD: 12345 "
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'TVPV HSD counts too')
        msg = "noTVPVHelp #12345 and stuff"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE), None)

        # Test JitBit Formats
        t_type = linker.ticket_types.JITBIT
        link_regex = linker.linker_types[t_type]['id_regex']
        msg = "JitBit 12345 first"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'JitBit 1st')
        msg = "JitBit: 12345"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'JitBit w/ :')
        msg = "Ticket #12345 and stuff"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'JitBit w/ #')
        msg = "ticket: 12345 "
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), '12345', 'JitBit lowercase counts too')
        msg = "noJitBit #12345 and stuff"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE), None)

        # Test Wiki Formats
        t_type = linker.ticket_types.WIKI
        link_regex = linker.linker_types[t_type]['id_regex']
        msg = "Wiki:page title:"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'page title', 'Wiki is first')
        msg = "Wiki : page title:"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'page title', 'Wiki is first')
        msg = "Wiki:wiki title:"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'wiki title', 'Wiki in name')
        msg = "Wiki: page title :"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'page title', 'Extra whitespace remove')
        msg = "Wiki: page title : with some more"
        self.assertEqual(re.search(link_regex, msg, re.IGNORECASE).group('ID'), 'page title', 'Extra whitespace remove')

    def test_create_link(self):
        linker = HtmlLinker()
        url = 'https://wiki.ith.intel.com/display/TVPV/TVPV+Home'
        self.assertEqual(linker.create_link(url, 'TVPV Wiki', 'bad_format'), '', "Nothing returned for unknown format")
        self.assertIn('TVPV+Home', linker.create_link(url, 'TVPV Wiki'), "HTML format")
        self.assertIn('TVPV+Home', linker.create_link(url, 'TVPV Wiki', 'wiki'), "Wiki Format Returned")

    def test_get_ids(self):
        linker = HtmlLinker()
        body = 'Rally US12345 and JitBit #103'
        links = linker.get_ids(body)
        self.assertEqual(len(links), 2)
        self.assertEqual(links['US12345'].l_type, linker.TicketType.RALLY)
        self.assertEqual(links['US12345'].l_id, 'US12345')
        self.assertEqual(links['103'].l_type, linker.TicketType.JITBIT)
        self.assertEqual(links['103'].l_id, '103')

        links = linker.get_ids(body, linker.TicketType.TVPVHELP)
        self.assertEqual(len(links), 0, "No TVPV Help types were found")

        links = linker.get_ids(body, linker.TicketType.RALLY)
        self.assertEqual(len(links), 1, "Rally types were found!")

        links = linker.get_ids(body, "badtypes")
        self.assertEqual(len(links), 0, "No badtypes were found")

        body = 'Wiki:page title: and Rally US12345 and JitBit #103 and Wiki:page2 title:'
        links = linker.get_ids(body)
        self.assertEqual(len(links), 4)

        body = 'Rally Story US12345 and again US12345'
        links = linker.get_ids(body)
        self.assertEqual(len(links), 1, 'Same ID only reported once')

        body = 'Rally Story US12345\n another US23456'
        links = linker.get_ids(body)
        self.assertEqual(len(links), 2, 'Looks across multiple lines for links')

    def test_replace_ids(self):
        linker = HtmlLinker()

        body = "Message with no IDs"
        self.assertEqual(linker.replace_ids(body), body)

        body = "Message with 'single' quotes"
        expected = "Message with &#39;single&#39; quotes"
        self.assertEqual(linker.replace_ids(body), expected)
        body = 'Message with "double" quotes'
        expected = "Message with &#34;double&#34; quotes"
        self.assertEqual(linker.replace_ids(body), expected)

        # Ensure Rally IDs are handled correctly
        body = "This is my Rally Story US12345 here"
        expected = 'This is my Rally Story <a href="' \
                   'https://rally1.rallydev.com/#/search?keywords=US12345">US12345</a> here'
        self.assertEqual(linker.replace_ids(body), expected)
        expected = 'This is my Rally Story [https://rally1.rallydev.com/#/search?keywords=US12345 '\
                   '| US12345] here'
        self.assertEqual(linker.replace_ids(body, 'wiki'), expected, "Wiki links work too")
        body = "This is my Rally Story US12345"
        expected = 'This is my Rally Story <a href="' \
                   'https://rally1.rallydev.com/#/search?keywords=US12345">US12345</a>'
        self.assertEqual(linker.replace_ids(body), expected)
        body = "This is my non-Rally Story POTUS12345"
        self.assertEqual(linker.replace_ids(body), body)

        # Ensure TVPV Helps are handled
        body = "This is my TVPV Help: 12345"
        expected = 'This is my TVPV Help: <a href="' \
                   'http://htd_tvpv_help.intel.com/Ticket/12345">12345</a>'
        self.assertEqual(linker.replace_ids(body), expected)

        # Test JitBit Handling
        body = "I have a Ticket 103 here"
        expected = 'I have a Ticket <a href="' \
                   'http://htd_tvpv_help.intel.com/Ticket/103">103</a> here'
        self.assertEqual(linker.replace_ids(body), expected, 'JitBit IDs collected as well')

        # Test Multiple Links
        body = "I worked on US12345 and JitBit 103 today"
        expected = 'I worked on <a href="https://rally1.rallydev.com/#/search?keywords=US12345">' \
                   'US12345</a> and JitBit <a href="http://htd_tvpv_help.intel.com/Ticket/' \
                   '103">103</a> today'
        self.assertEqual(linker.replace_ids(body), expected, 'Multiple links added')

        body = "I worked on US12345 and US23456 today"
        expected = 'I worked on <a href="https://rally1.rallydev.com/#/search?keywords=US12345">' \
                   'US12345</a> and ' \
                   '<a href="https://rally1.rallydev.com/#/search?keywords=US23456">US23456</a>' \
                   ' today'
        self.assertEqual(linker.replace_ids(body), expected, 'Multiple links of same type added')

        # Real case seen, user includes the same story twice
        body = "I worked on US12345 and US12345 twice today"
        expected = 'I worked on <a href="https://rally1.rallydev.com/#/search?keywords=US12345">' \
                   'US12345</a> and ' \
                   '<a href="https://rally1.rallydev.com/#/search?keywords=US12345">US12345</a>' \
                   ' twice today'
        self.assertEqual(linker.replace_ids(body), expected, 'Same story mentioned multiple times')


class TestPatternHeader(TestCase):

    def setUp(self):
        self.pinlist = ['xxTDO', 'xxMYLONGERPINNAME', 'xxTHIRDPIN']
        self.pin_header = PinHeader(self.pinlist)

    def test_CreatePinHeader(self):
        self.assertIsNotNone(self.pin_header, "Check for PinHeader created")

    def test_getHeaderString(self):
        getbackstr = """\
 x{space}
 x{space}
 M{space}
 Y{space}
 L{space}
 O{space}
 N{space}
 Gx
 Ex
 RT
 PH
 II
xNR
xND
TAP
DMI
OEN
""".format(space=' ')
        print("__b__\n" + getbackstr + "__e__")
        res = self.pin_header.getHeaderString(comment_char='', spaces=0)
        print("__b__\n" + res + "__e__")
        self.assertEqual(res.split('\n'), getbackstr.split('\n'))

        getbackstr = """\
//           x{space}
//           x{space}
//           M{space}
//           Y{space}
//           L{space}
//           O{space}
//           N{space}
//           Gx
//           Ex
//           RT
//           PH
//           II
//          xNR
//          xND
//          TAP
//          DMI
//          OEN
""".format(space=' ')
        print("__b__\n" + getbackstr + "__e__")
        res = self.pin_header.getHeaderString(comment_char='//', spaces=10)
        print("__b__\n" + res + "__e__")
        self.assertEqual(res.split('\n'), getbackstr.split('\n'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
    exit(0)
