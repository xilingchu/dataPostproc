from setuptools import setup

setup(
        name='dataPostproc',
        version='0.1.0',
        description='Postprocessing code for DNS data.',
        requires=['h5py'],
        url='http://github.com/xilingchu/dataPostproc',
        author='Xi Lingchu',
        author_email='xilingchu@163.com',
        license='MIT',
        packages=['dataPostproc', 'dataPostproc.output', 'dataPostproc.utils', 'dataPostproc.hdfview'],
        scripts=['scripts/dataPostproc']
        )
