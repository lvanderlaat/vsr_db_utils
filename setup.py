from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name             = 'vsr_db_utils',
    version          = '0.1',
    description      = 'Utils to export waves for VSR',
    long_description =  readme(),
    url              = 'https://github.com/OVSICORI-UNA/vsr_db_utils',
    author           = 'Leonardo van der Laat',
    author_email     = 'leonardo.vanderlaat.munoz@una.cr',
    packages         = ['vsr_db_utils'],
    install_requires = [
    ],
    scripts          = [
        'bin/VT-filter-db',
        'bin/antelope-catalog',
        'bin/check-swarm',
        'bin/db-to-lakiy',
        'bin/filter-db',
        'bin/lakiy-db-stats',
        'bin/pick',
        'bin/pick-tectonic',
        'bin/trim',
        'bin/trim-tectonic',
        'bin/txt-to-swarm',
        'bin/waves-add-CVTR',
    ],
    zip_safe         = False
)
