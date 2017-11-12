from distutils.core import setup
setup(
  name = 'pytouchline',
  packages = ['pytouchline'],
  version = '0.4',
  description = 'A Roth Touchline interface library',
  author = 'Aksel Bondoe',
  author_email = 'aksel.bondoe@gmail.com',
  license='MIT',
  url = 'https://github.com/abondoe/pytouchline',
  download_url = 'https://github.com/abondoe/pytouchline/archive/0.4.tar.gz',
  keywords = ['Roth', 'Touchline', 'Home Assistant', 'hassio', "Heat pump"],
  classifiers = [
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
  ],
  install_requires=['httplib2']
)