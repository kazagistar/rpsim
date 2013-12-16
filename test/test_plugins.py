
import unittest
from unittest.mock import patch
import sys

from plugin import PluginSet

class TestPlugins(unittest.TestCase):
    def setUp(self):
        self.path_patch = patch('plugin.PluginSet', _plugin_path='test.plugins.')
        self.module_patch = patch.dict(sys.modules)
        self.path_patch.__enter__()
        self.module_patch.__enter__()

    def tearDown(self):
        self.module_patch.__exit__()
        self.path_patch.__exit__()

    def test_loadPlugins(self):
        a = PluginSet('test2')
        self.assertIsNotNone(a.events['test'])
        
    def test_callPlugins(self):
        testset = PluginSet('test1')
        called = set()
        testset.trigger(event='test', param=called)

        self.assertEqual(called, set([1,2]))
        
    def test_multiplePlugins(self):
        testset = PluginSet('test1', 'test2')
        called = set()
        testset.trigger(event='test', param=called)
        
        self.assertEqual(called, set([1,2, 5]))

    def test_multiplePluginSets(self):
        testset1, testset2 = PluginSet('test1'), PluginSet('test2')
        called1, called2 = set(), set()
        testset1.trigger('fake', param=called1)
        testset2.trigger('test', param=called2)
        
        self.assertEqual(called1, set([3,4]))
        self.assertEqual(called2, set([5]))
