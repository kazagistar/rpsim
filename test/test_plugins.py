"""

 .. moduleauthor Jakub Gedeon

"""
import unittest
import sys
import plugins

class TestPlugins(unittest.TestCase):
    def setUp(self):
        import plugins

    def tearDown(self):
        try:
            del sys.modules['plugins']
        except KeyError:
            pass

    def test_createPlugins(self):
        plugins.plugin("t1")
        @plugins.event
        def test(param, **_):
            pass
        
        self.assertIsNotNone(plugins._plugins["t1"])
        self.assertIsNotNone(plugins._events["test"])
        
    def test_callPlugins(self):
        plugins.plugin("t1")
        @plugins.event
        def test(param, **_):
            param.append("t1")
            
        plugins.plugin("t2")
        @plugins.event
        def test(param, **_):
            param.append("t2")
            
        plugins.plugin("t3")
        @plugins.event
        def test(param, **_):
            param.append("t3")
            
        testset = plugins.PluginSet("t1", "t2")
        called = []
        testset.trigger(event="test", param=called)
        
        self.assertEqual(called, ["t1", "t2"])
    
