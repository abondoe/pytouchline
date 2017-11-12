from distutils.core import setup
setup(
  name = 'touchline',
  packages = ['touchline'],
  version = '0.3',
  description = 'A Roth Touchline interface library',
  author = 'Aksel Bondoe',
  author_email = 'aksel.bondoe@gmail.com',
  license='MIT',
  url = 'https://github.com/abondoe/touchline',
  download_url = 'https://github.com/abondoe/touchline/archive/0.3.tar.gz',
  keywords = ['Roth', 'Touchline', 'Home Assistant', 'hassio', "Heat pump"],
  classifiers = [
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
  ],
  install_requires=['httplib2']
)