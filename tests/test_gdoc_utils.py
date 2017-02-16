from __future__ import absolute_import

import os
import unittest

import misc.gdoc_utils as gdoc_utils


class TestGdocUtils(unittest.TestCase):
    def test_strip_invalid_characters(self):
        """ Test cases contain most common illegal characters, attempts to create file"""
        a = r'som+?e<file>th`a`-t:con*ta>ins"inv#a%lid/\chara cters'
        b = r's!ome|more?in=v|a`lid*char&{a}c<ters\\and\\\combi$nations///\\\/'
        a, b = gdoc_utils.strip_invalid_characters(a), gdoc_utils.strip_invalid_characters(b)
        try:
            f1 = open(a, 'a')
            f2 = open(b, 'a')
        except IOError:
            raise
        else:
            f1.close()
            f2.close()
            os.remove(f1.name)
            os.remove(f2.name)

    def test_strip_path_extension(self):
        """ Tests cases that could cause issues with stripping extension """
        path1 = r'c:\program files\stuff\some.file.with.periods.txt'
        path2 = r'c:\program files\stuff\normal.txt'
        path3 = r'c:\program files\stuff\some.periods.txt'
        path4 = r'some.file.with.periods.txt'
        path5 = r'~/some/file/where\ a space exists.pdf'
        path6 = r'./out.there.pdf'

        self.assertEquals(gdoc_utils.strip_path_extension(path1), 'some.file.with.periods')
        self.assertEquals(gdoc_utils.strip_path_extension(path2), 'normal')
        self.assertEquals(gdoc_utils.strip_path_extension(path3), 'some.periods')
        self.assertEquals(gdoc_utils.strip_path_extension(path4), 'some.file.with.periods')
        self.assertEquals(gdoc_utils.strip_path_extension(path5), ' a space exists')
        self.assertEquals(gdoc_utils.strip_path_extension(path6), 'out.there')

    def test_choose_file_dialog(self):
        """ Hides the root pane and calls tkFileDialog.askopenfile(), no need to test"""
        pass

    def test_ensure_path(self):
        """ Tests creation of new directory, and trying to create directory that already exists"""
        try:
            gdoc_utils.ensure_path('does/not/exist/for/sure')
            gdoc_utils.ensure_path('does/not/exist/for/sure')
        except IOError:
            raise
        else:
            os.removedirs('does/not/exist/for/sure')
            pass

    def test_remove_directory(self):
        """ Just wraps shutil.rmtree() in a try/except to ignore files that don't exist"""
        pass

    def test_temp_directory(self):
        """ Assert temporary directory is writable, and successfully removed at end"""
        tempdir = ''
        with gdoc_utils.temp_directory() as td:
            tempdir = td
            filename = r'{}\{}'.format(td, 'temp.txt')
            with open(filename, 'w') as f:
                f.write('msg')

        self.assertFalse(os.path.exists(td))
        self.assertFalse(os.path.isfile(filename))


if __name__ == '__main__':
    unittest.main()
