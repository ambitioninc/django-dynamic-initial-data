

class InitialDataCircularDependency(Exception):
    def __init__(self, *args, **kwargs):
        dep = kwargs.get('dep')
        call_list = kwargs.get('call_list')
        call_list += [dep]
        for i, item in enumerate(call_list):
            if item == dep:
                call_list[i] = '\033[1m{0}\033[0m'.format(item)
        call_lines = [
            '{0}{1}'.format('--' * i, item)
            for i, item in enumerate(call_list)
        ]
        error_str = 'Circular dependency found\n{0}'.format('\n'.join(call_lines))
        super(InitialDataCircularDependency, self).__init__(error_str)


class InitialDataMissingApp(Exception):
    def __init__(self, *args, **kwargs):
        dep = kwargs.get('dep')
        error_str = 'Missing dependency {0}'.format(dep)
        super(InitialDataMissingApp, self).__init__(error_str)
