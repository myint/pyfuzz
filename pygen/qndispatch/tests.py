import unittest

from . import qndispatch


class DispatchTest(unittest.TestCase):

    def testDispatchOn(self):
        class TestClass(object):

            @qndispatch.on("name")
            def test(self, name):
                self.fail("Illegal call to dispatch.on function")

            @test.when(str)
            def test(self, name):
                pass

        t = TestClass()
        t.test("n")
        t.test(name="n")

        try:
            t.test([])
            self.fail("Dispatch with unregistered type did not fail.")
        except qndispatch.InvalidArgException:
            pass

    def testTargetMismatch(self):
        try:
            class TestClass(object):

                @qndispatch.on("name")
                def test(self, name):
                    self.fail("Illegal call to dispatch.on function")

                @test.when(str)
                def test(self, name, mismatch):
                    pass
            self.fail("Target argument mismatch not found.")
        except qndispatch.DispatchTargetException:
            pass


if __name__ == "__main__":
    unittest.main()
