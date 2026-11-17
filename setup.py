from setuptools import setup
setup(
  name = 'pytouchline_extended',
  packages = ['pytouchline_extended'],
  version = "$GITHUB_REF_NAME",
  description = 'A Roth Touchline interface library',
  long_description="A simple helper library for controlling a Roth Touchline heat pump controller",
  author = 'Peter Brondum',
  license='MIT',
  url = 'https://github.com/brondum/pytouchline',
  keywords = ['Roth', 'Touchline', 'Home Assistant', 'hassio', "Heat pump"],
  classifiers = [
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.10',
	'Programming Language :: Python :: 3.11',
	'Programming Language :: Python :: 3.12',
	'Programming Language :: Python :: 3.13',
  'Programming Language :: Python :: 3.14',
	'Typing :: Typed',
  ],
  package_data={'pytouchline_extended': ['py.typed']},
  python_requires='>=3.10',
  install_requires=['httpx', 'faust-cchardet']
)
