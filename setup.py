from setuptools import setup


setup(
    version="0.0",
    name='stemmabench',
    packages=['stemmabench'],
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'generate = stemmabench.cli:app',
        ]}
)
