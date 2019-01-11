from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt") as f:
    REQUIREMENT = f.read().split("\n")

setup(
    name='xray',
    version='1.1',
    description='A module to support infrasys self service',
    long_description=LONG_DESCRIPTION,
    author='Dan Quackenbush',
    author_email='danquack@gmail.com',
    packages=find_packages(),  # same as name
    install_requires=REQUIREMENT,
    python_requires='>=3.4',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
