from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 6):
    print('trumppet requires python3 version >= 3.6.')
    sys.exit(1)

setup(
    name='trumppet',
    version="0.0.1",
    description='Donald Trump tweet analyzer',
    url='https://github.com/chrismeyers/trumppet',
    author='Chris Meyers',
    author_email='cm.02.93@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'trumppet-client=trumppetclient:cli',
            'trumppet-server=trumppetserver:cli'
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
