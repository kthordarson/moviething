from setuptools import setup

setup(
    name='moviething',
    version='1.0',
    packages=['moviething', 'moviething.modules', 'modules'],
    package_dir={'': 'moviething'},
    url='https://github.com/kthordarson/moviething',
    license='GNU',
    author='kthordarson',
    author_email='kthordarson@gmail.com',
    description='a thing to manage my movie collection',
)
