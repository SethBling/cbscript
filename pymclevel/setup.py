from setuptools import setup
from setuptools.extension import Extension
from Cython.Distutils import build_ext

import numpy

version = '0.1'

install_requires = [
    # -*- Extra requirements: -*-
    "numpy",
    "pyyaml",
    ]

ext_modules = [Extension("_nbt", ["_nbt.pyx"])]

setup(name='pymclevel',
      version=version,
      description="Python library for reading Minecraft levels",
      long_description=open("./README.txt", "r").read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='minecraft',
      author='David Vierra',
      author_email='codewarrior0@gmail.com',
      url='https://github.com/mcedit/pymclevel',
      license='MIT License',
      package_dir={'pymclevel': '.'},
      packages=["pymclevel"],
      ext_modules=ext_modules,
      include_dirs=numpy.get_include(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      cmdclass={'build_ext': build_ext},
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      mce.py=pymclevel.mce:main
      """,
      )
