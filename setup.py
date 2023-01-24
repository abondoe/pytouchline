from distutils.core import setup
setup(
  name = 'pytouchlineplus',
  packages = ['pytouchlineplus'],
  version = '0.8',
  description = 'A Roth Touchline interface library',
  author = 'Mikkel Pilehave Jensen',
  author_email = 'pilehave@gmail.com',
  license='MIT',
  url = 'https://github.com/pilehave/pytouchlineplus',
  download_url = 'https://github.com/pilehave/pytouchlineplus/archive/0.8.tar.gz',
  keywords = ['Roth', 'Touchline', 'Home Assistant', 'hassio', "Heat pump"],
  classifiers = [
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
  ],
  install_requires=['httplib2', 'cchardet']
)
