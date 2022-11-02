from setuptools import setup, find_packages

with open('requirements.txt', mode='r') as f:
    INSTALL_REQUIRES = [requirement
                        for requirement in f.read().split('\n')
                        if requirement != ''
                        ]

setup(name='red-moose',
      version='0.1',
      description='Houses the data ingestion, price and risk modeling backend.',
      url='ys',
      author='axs',
      packages=find_packages(),
      package_dir={'': 'lib'},
      install_requires=INSTALL_REQUIRES,
      zip_safe=False
      )
