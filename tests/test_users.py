import unittest
import os

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'

class UserTests(unittest.TestCase):
# place your test functions here

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # each test should start with 'test'
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def test_user_setup(self):
        new_user = User('michael', 'michael@herman.org', 'michaelherman')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == 'michael'


    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data = dict(name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )

    def register_exemple(self):
        self.app.get('register/', follow_redirects=True)
        return self.register("Michael", "michael@realpython.com", "python","python")

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.',  response.data)


    def test_users_can_login(self):
        self.register_exemple()
        response = self.login('Michael','python')
        self.assertIn(b'Welcome!', response.data)


    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login to access your task list.', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)


    def test_invalid_form_data(self):
        self.register_exemple()
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_user_registration(self):
        response = self.register_exemple()
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_user_duplicate_registration_error(self):
        self.register_exemple()
        response = self.register_exemple()
        self.assertIn(b'That username and/or email already exist.', response.data)

    def test_logged_in_users_can_logout(self):
        self.register_exemple()
        self.login("Michael", "python")
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye!', response.data)

    def test_logged_in_out_users_can_not_access_tasks_page(self):
        self.register_exemple()
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)
        self.login("Michael","python")
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_default_user_role(self):

        db.session.add(
            User(
                "Johnny",
                "john@doe.com",
                "johnny"
            )
        )

        db.session.commit()

        users = db.session.query(User).all()
        print(users)
        for user in users:
            self.assertEquals(user.role,'user')



if __name__ == '__main__':
    unittest.main()
