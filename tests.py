import unittest
import mock
import util


class TestProxy(unittest.TestCase):

    @mock.patch('util.pooler')
    def test_create(self, mock_pooler):
        pool = util.PoolProxy(None)
        pool2 = util.PoolProxy(None)
        pool.attr1 = 1
        pool2.attr1 = 2
        self.assertTrue(pool == pool2)
        self.assertEqual(pool.attr1, pool2.attr1)
        self.assertEqual(pool.attr1, 2)


if __name__ == '__main__':
    unittest.main()
