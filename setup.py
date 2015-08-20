from setuptools import setup

setup(name='google_analytics_dataframes',
      version='0.1',
      description='Functions for querying and returning DataFrames from Google Analytics',
      url='http://github.com/coej/google_analytics_dataframes',
      author='Chris Jenkins',
      author_email='chrisoej@gmail.com',
      license='MIT',
      packages=['google_analytics_dataframes'],
      install_requires=[
          'ipython',
          'pandas',
          'oauth2client',
          'google-api-python-client',
          'future'
      ],
      # dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0']
      # for stuff not on pypi

      include_package_data=True,
      # use this if I want to copy over things in MANIFEST.in when installing

      zip_safe=False)