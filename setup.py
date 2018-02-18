from setuptools import setup, find_packages
import os
import sys

if sys.version_info < (3, 6):
    print('trumppet requires python3 version >= 3.6.')
    sys.exit(1)

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "trumppet", "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name='trumppet',
    version=about['__version__'],
    description='Donald Trump tweet analyzer',
    url='https://github.com/chrismeyers/trumppet',
    author='Chris Meyers',
    author_email='cm.02.93@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'trumppet=trumppet:cli'
        ],
    },
    install_requires=[
        'mcgpyutils',
        'python-twitter',
        'pymongo',
        'click'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
)
