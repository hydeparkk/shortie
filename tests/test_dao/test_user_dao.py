from tornado.testing import gen_test

from tests.shortie_tests_common import DaoTestBase

from shortie.dao import User, DaoException


class TestUserDao(DaoTestBase):

    def setUp(self):
        super().setUp()

        async def clear_colection(db, collection):
            await db[collection].delete_many({})

        self.io_loop.add_callback(
            clear_colection, self.db, User.COLLECTION_NAME
        )

    @gen_test
    async def test_save_user_missing_parameters(self):
        user = User(self.db, {})

        with self.assertRaises(DaoException):
            await user.save_user()

    @gen_test
    async def test_save_user_empty_parameters(self):
        user = User(self.db, {'email': '', 'password': ''})

        with self.assertRaises(DaoException):
            await user.save_user()

    @gen_test
    async def test_save_user(self):
        user = User(
            self.db, {'email': 'test@tst.com', 'password': 'simplepass'}
        )
        try:
            await user.save_user()
        except DaoException:
            self.fail('save_user() raised exception unexpectedly!')

    @gen_test
    async def test_user_already_exists(self):
        await User(
            self.db,
            {'email': 'existing_user@tst.com', 'password': 'simplepass'}
        ).save_user()

        with self.assertRaises(DaoException):
            await User(
                self.db,
                {'email': 'existing_user@tst.com', 'password': 'anotherpass'}
            ).save_user()

    @gen_test
    async def test_validate_passed(self):
        user = User(
            self.db,
            {'email': 'existing_user@tst.com', 'password': 'simplepass'}
        )
        await user.save_user()

        try:
            await user.validate_user()
        except DaoException:
            self.fail('validate_user() raised exception unexpectedly!')

    @gen_test
    async def test_incorrect_password(self):
        user = User(
            self.db,
            {'email': 'existing_user@tst.com', 'password': 'simplepass'}
        )
        await user.save_user()

        user.password = 'otherpass'

        with self.assertRaises(DaoException):
            await user.validate_user()

    @gen_test
    async def test_validete_unexisting_user(self):
        with self.assertRaises(DaoException):
            await User(
                self.db,
                {'email': 'tst.com', 'password': 'simplepass'}
            ).validate_user()
