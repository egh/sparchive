from setuptools import setup, find_packages

setup(name='sparchive',
      version="0.1.1",
      description="simple personal archive",
      classifiers=[
          "Operating System :: OS Independent",
          "Programming Language :: Python",
      ],
      author='Erik Hetzner',
      author_email='egh@e6h.org',
      url='https://bitbucket.org/egh/sparchive',
      packages=find_packages(exclude=[
          'tests']),
      entry_points={
          'console_scripts': [
              'sparchive = sparchive.cli:main'
          ]
      },
      install_requires=[],
      test_suite='tests',
      )
