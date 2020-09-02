import disdat.api as api
from disdat.pipe import PipeTask
import luigi


data_context = 'example-context'


class PipeWithParams(PipeTask):

    n = luigi.IntParameter()

    def pipe_requires(self):
        self.set_bundle_name('pipe_with_params')

    def pipe_run(self):
        print('-------------------')
        print("pipe_with_params n:{} is Running!".format(self.n))
        print('-------------------')
        print()

        return self.n


if __name__ == '__main__':
    api.apply(data_context, PipeWithParams, params={'n': 10})

    api.apply(data_context, PipeWithParams, params={'n': 20})
