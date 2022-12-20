from setuptools import setup, find_packages


setup(
    name='pyjsa',
    version='0.0.1',
    license='GNU GPL-3.0',
    author="Danut-Valentin Dinu",
    author_email='dadinu@student.ethz.ch',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/dadinu/pyjsa',
    keywords='simulation photons LNOI waveguides PPLN JSA PMF PEF purity heralding efficiency',
    install_requires=[
          'numpy',
          'scipy',
          'PyQt5',
          'pyqtgraph'
      ],

)