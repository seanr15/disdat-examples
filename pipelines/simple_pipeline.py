import disdat.api as api
from disdat.pipe import PipeTask

data_context = 'example-context'


class SimplePipeline(PipeTask):
    def pipe_requires(self):
        self.set_bundle_name('simple_pipeline')

    def pipe_run(self):
        print('-------------------')
        print('Simple Pipeline is Running!')
        print('-------------------')
        print()

        return 2

if __name__ == '__main__':
    api.apply(data_context, 'SimplePipeline')
