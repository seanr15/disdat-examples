import disdat.api as api
from disdat.pipe import PipeTask
import pandas as pd

data_context = 'example-context'


class ReturnTargets(PipeTask):

    def pipe_requires(self):
        self.set_bundle_name('return_targets')

    def pipe_run(self):
        print('-------------------')
        print('return_targets is Running!')
        print('-------------------')
        print()

        data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
        df = pd.DataFrame(data)

        target = self.create_output_file('df.csv')
        with target.temporary_path() as temp_output_path:
            df.to_csv(temp_output_path)

        return {'df': [target]}

if __name__ == '__main__':
    api.apply(data_context, 'ReturnTargets', params={'n': 10})
