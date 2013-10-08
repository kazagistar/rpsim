"""

 .. moduleauthor Jakub Gedeon

"""
import unittest
import sys
import plugin

class TestPlugins(unittest.TestCase):
    def setUp(self):
        import plugin

    def tearDown(self):
        try:
            del sys.modules['plugins']
        except KeyError:
            pass

    def test_createPlugins(self):
        plugin.plugin("t1")
        @plugin.event
        def test(param, **_):
            pass
        
        self.assertIsNotNone(plugin._plugins["t1"])
        self.assertIsNotNone(plugin._events["test"])
        
    def test_callPlugins(self):
        plugin.plugin("t1")
        @plugin.event
        def test(param, **_):
            param.append("t1")

        plugin.plugin("t2")
        @plugin.event
        def test(param, **_):
            param.append("t2")

        plugin.plugin("t3")
        @plugin.event
        def test(param, **_):
            param.append("t3")

        testset = plugin.PluginSet("t1", "t2")
        called = []
        testset.trigger(event="test", param=called)

        self.assertEqual(called, ["t1", "t2"])
