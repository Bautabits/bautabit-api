import unittest
import hombit


class SimulatorTest(unittest.TestCase):
    sim = hombit.Simulator()

    def test_get_device_type_works(self):
        self.assertEquals("Simulator", self.sim.get_device_type())

    def test_init_has_generated_device_id(self):
        self.assertIsNotNone(self.sim.get_device_id())

    def test_invalid_key__get_io_pin__throws_key_error(self):
        try:
            self.sim.get_io_pin('foo')
            self.fail();
        except KeyError:
            return

    def test_invalid_key__set_io_pin__throws_key_error(self):
        try:
            self.sim.set_io_pin('foo', True)
            self.fail();
        except KeyError:
            return


if __name__ == "__main__":
    unittest.main()
