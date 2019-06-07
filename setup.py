from setuptools import setup, find_packages


setup(
    name='disdat-examples',
    version='0.0.1rc0',

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        'disdat>=0.8.3rc1',
        'jupyter',
        'pandas'
    ]
)
