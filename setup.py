from setuptools import setup
from distutils.util import convert_path


# Hack to get around version dependency problems
# Taken from: https://stackoverflow.com/a/24517154
main_ns = {}
ver_path = convert_path('CYLGame/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)


setup(name='CYLGame',
      version=main_ns["version"],
      description='UMDCYL Game Framework',
      url='https://github.com/umdlars/CYLGame',
      author='Jonathan Beaulieu',
      author_email='123.jonathan@gmail.com',
      license='MIT',
      packages=['CYLGame'],
      zip_safe=False,
      classifiers=[
            # Complete list of classifiers: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 2.7",
      ]
      )
