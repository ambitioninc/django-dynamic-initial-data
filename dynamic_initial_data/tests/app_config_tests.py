from app_init import BaseAppInit, detect_dependency_cycles


class Test_detect_dependencies(TestCase):
    def test_with_cycles(self):
        class mockAppInit_1(object):
            dependencies = ['mockAppInit_2']

        class mockAppInit_2(object):
            dependencies = ['mockAppInit_3']

        class mockAppInit_3(object):
            dependencies = ['mockAppInit_1']

        def mock_app_loader(app_name):
            if app_name is 'mockAppInit_1':
                return mockAppInit_1
            if app_name is 'mockAppInit_2':
                return mockAppInit_2
            if app_name is 'mockAppInit_3':
                return mockAppInit_3
            return None

        self.assertEqual(
            (True, ['mockAppInit_1', 'mockAppInit_2', 'mockAppInit_3', 'mockAppInit_1']),
            detect_dependency_cycles('mockAppInit_1', app_loader=mock_app_loader))

    def test_without_cycles(self):
        class mockAppInit_1(object):
            dependencies = ['mockAppInit_2']

        class mockAppInit_2(object):
            dependencies = ['mockAppInit_3']

        class mockAppInit_3(object):
            dependencies = []

        def mock_app_loader(app_name):
            if app_name is 'mockAppInit_1':
                return mockAppInit_1
            if app_name is 'mockAppInit_2':
                return mockAppInit_2
            if app_name is 'mockAppInit_3':
                return mockAppInit_3
            return None

        self.assertEqual(
            (False, []),
            detect_dependency_cycles('mockAppInit_1', app_loader=mock_app_loader))


class TestUpdateDependencies(TestCase):
    def test_updates(self):
        update_static_call_history = []

        class mockAppInit(BaseAppInit):
            dependencies = []

            def update_static(self_, *args, **kwargs):
                update_static_call_history.append(self_.__class__.__name__)

        class mockAppInit_1(mockAppInit):
            dependencies = ['mockAppInit_2', 'mockAppInit_4']

        class mockAppInit_2(mockAppInit):
            dependencies = ['mockAppInit_3']

        class mockAppInit_3(mockAppInit):
            dependencies = ['mockAppInit_5']

        class mockAppInit_4(mockAppInit):
            dependencies = []

        class mockAppInit_5(mockAppInit):
            dependencies = []

        def mock_app_loader(app_name):
            if app_name is 'mockAppInit_1':
                return mockAppInit_1
            if app_name is 'mockAppInit_2':
                return mockAppInit_2
            if app_name is 'mockAppInit_3':
                return mockAppInit_3
            if app_name is 'mockAppInit_4':
                return mockAppInit_4
            if app_name is 'mockAppInit_5':
                return mockAppInit_5
            return None

        mockAppInit_1().update(app_loader=mock_app_loader)

        self.assertEqual(
            ['mockAppInit_5', 'mockAppInit_3', 'mockAppInit_2', 'mockAppInit_4', 'mockAppInit_1'],
            update_static_call_history)
