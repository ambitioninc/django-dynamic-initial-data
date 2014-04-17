from dynamic_initial_data.base import BaseInitialData

mock_null_value = None

class MockClass(object):
    pass


class MockInitialData(BaseInitialData):
    def update_static(self, *args, **kwargs):
        return super(MockInitialData, self).update_static(*args, **kwargs)
