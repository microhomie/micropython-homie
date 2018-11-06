from setuptools import setup
import sdist_upip

from homie import __version__


setup(
    name='microhomie',
    version=__version__.decode(),
    description='MicroPython implementation of the Homie MQTT convention for IoT.',
    long_description=open('README.rst').read(),
    url='https://github.com/microhomie/microhomie',
    author='Microhomie Developers',
    author_email='contact@microhomie.com',
    maintainer='Microhomie Developers',
    maintainer_email='contact@microhomie.com',
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['homie', 'homie.node'],
    install_requires=['micropython-umqtt.simple'],
)
