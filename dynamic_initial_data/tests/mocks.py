from dynamic_initial_data.base import BaseInitialData

mock_null_value = None


class MockClass(object):
    pass


class MockInitialData(BaseInitialData):
    def update_initial_data(self):
        pass


class MockOne(BaseInitialData):
    pass


class MockTwo(BaseInitialData):
    dependencies = ['MockOne']


class MockThree(BaseInitialData):
    dependencies = ['MockThree']
