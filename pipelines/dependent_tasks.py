import disdat.api as api
from disdat.pipe import PipeTask


data_context = 'example-context'


class A(PipeTask):
    def pipe_requires(self):
        self.set_bundle_name('a')

    def pipe_run(self):
        print('-------------------')
        print('A is Running!')
        print('-------------------')
        print()

        return 2


class B(PipeTask):
    def pipe_requires(self):
        self.set_bundle_name('b')
        self.add_dependency('a', A, params={})

    def pipe_run(self, a):
        print('-------------------')
        print('B is Running!')
        print('-------------------')
        print()

        return a ** 2


if __name__ == '__main__':
    api.apply(data_context, B)
