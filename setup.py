import setuptools

setuptools.setup(
    name='wabbit',
    url='https://github.com/zzhengnan/wabbit',
    author='Zhengnan Zhao',
    description='Python implementation of the Wabbit language',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': ['wabbit=wabbit.main:main']},
    python_requires='>=3.8',
    extras_require={
        'dev': ['coverage', 'ipython', 'mypy', 'pre-commit', 'pytest', 'ruff'],
    },
)
