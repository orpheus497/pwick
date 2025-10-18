"""
Setup script for pwick - A local-first password manager.
"""

from setuptools import setup, find_packages
import os

# Read the README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name='pwick',
    version='1.0.0',
    author='orpheus497',
    author_email='',
    description='A simple, secure, and 100% local password manager',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/orpheus497/pwick',
    project_urls={
        'Bug Reports': 'https://github.com/orpheus497/pwick/issues',
        'Source': 'https://github.com/orpheus497/pwick',
    },
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Security',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications :: Qt',
    ],
    python_requires='>=3.7',
    install_requires=[
        'PyQt5==5.15.10',
        'cryptography==41.0.7',
        'argon2-cffi==23.1.0',
        'pyperclip==1.8.2',
    ],
    entry_points={
        'console_scripts': [
            'pwick=pwick.__main__:main',
        ],
        'gui_scripts': [
            'pwick-gui=pwick.__main__:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='password manager security encryption local-first privacy',
)
