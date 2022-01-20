from setuptools import setup, find_packages


setup(
    name='disdat-examples',
    version='0.0.2',

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
          'disdat-luigi>=1.0.0rc1'
        , 'pandas==0.25.3'
        , 'scikit-learn'
        , 'pyspark'
        , 'jupyter'
        #, 'spacy'
        #, 'tensorflow'
        #, 'tensorflow-datasets'
    ]
)
