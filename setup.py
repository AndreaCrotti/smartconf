from setuptools import setup, find_packages

package = 'smartconf'
version = '0.1'

setup(name=package,
      author="Andrea Crotti",
      license='BSD',
      keywords="configuration",
      packages=find_packages('.'),
      version=version,
      description="Simple wrapper around ConfigParser",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
      ]
)
