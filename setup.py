from setuptools import setup, find_packages

setup(
    name='patisson_request',
    version='1.6.2',
    packages=find_packages(),
    install_requires=[
        "httpx",
        "pydantic",
        "redis"
    ],
    author='EliseyGodX',
    description='a library that regulates the interaction between microservices',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Patisson-Company/_Request',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)