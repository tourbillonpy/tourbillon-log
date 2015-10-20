from setuptools import setup, find_packages
setup(
    name='tourbillon-log',
    version='0.3',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['watchdog==0.8.3'],
    namespace_packages=['tourbillon']
)
