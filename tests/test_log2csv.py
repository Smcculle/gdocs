from __future__ import absolute_import

import unittest
from collections import OrderedDict

import log2csv


class TestLog2Csv(unittest.TestCase):
    def test_rename_keys(self):
        """ Test mappings are being applied recursively and appropriately, and values unchanged"""
        d1 = log2csv.rename_keys({})
        d2 = log2csv.rename_keys({'ty': 'st', 's': 'abc', 'ibi': 5, 'z':
            {'ds': 'del', 'nokey': 'fm'}, 'empty': {}})
        d3 = log2csv.rename_keys({'ty': 1, 'l2': {'l3': {'das_a': 'anchor_val'}}})

        remap1 = self.recursive_ordered_dict({})
        remap2 = self.recursive_ordered_dict({'type': 'st', 'string': 'abc', 'ins_index': 5,
                                              'z': {'del': 'del', 'nokey': 'fm'}, 'empty': {}})
        remap3 = self.recursive_ordered_dict({'type': 1, 'l2': {'l3': {'ds_anchor': 'anchor_val'}}})

        self.assertTrue(d1.keys().sort() == remap1.keys().sort()
                        and d1.values().sort() == remap1.values().sort())
        self.assertTrue(d2.keys().sort() == remap2.keys().sort()
                        and d2.values().sort() == remap2.values().sort())
        self.assertTrue(d3.keys().sort() == remap3.keys().sort()
                        and d3.values().sort() == remap3.values().sort())

    def recursive_ordered_dict(self, dict_):
        dict_ = OrderedDict(dict_)
        for key in dict_.keys():
            if isinstance(dict_[key], dict):
                dict_[key] = self.recursive_ordered_dict(dict_[key])

        return dict_


if __name__ == '__main__':
    unittest.main()
