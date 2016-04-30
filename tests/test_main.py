# project/test_main.py

import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'

class MainTests(unittest.TestCase):

        ##########################
        ### setup and teardown ###
        ##########################

        # exectued prior to each test
        def setUp(self):
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                    os.path.join(basedir, TEST_DB)
            app.config['DEBUG'] = False
            self.app = app.test_client()
            db.create_all()

        #executed after each test
        def tearDown(self):
            db.session.remove()
            db.drop_all()

        ######################
        ### helper methods ###
        ######################

        def login(self, name, password):
            return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

        ###############
        #### tests ####
        ###############

        def test_404_error(self):
            response = self.app.get('/this-route-does-not-exist/')
            self.assertEqual(response.status_code, 404)
            self.assertIn(b'Sorry. There\'s nothing here.',response.data)

if __name__ == "__main__":
    unittest.main()