try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='GridMonitor',
    version="0.8.2-2",
    description='A monitor for Grids based on the NorduGrid ARC middleware',
    long_description=""" \
	The GridMonitor, which has been developed within the AAA/SWITCH SMSCG project,
	consolidates activly and passively collected information about the Grids. The 
	collected information is processed (including basic accouting and rrd plotting)
	and displayed in a unified and customized view to users, to site administrators, 
	and VO/Grid to administrators.  
	The current GridMonitor is relies on AAI, i.e. on a federated Authentication and 
	Authorization Infrastructure. """,
    author='SMSCG Project',
    author_email='grid@switch.ch',
    url='http://www.smscg.ch',
    license='BSD, see shipped LICENSE file',
    install_requires=["Pylons>=0.9.6.2", "SQLAlchemy>=0.5"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'gridmonitor': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'gridmonitor': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = gridmonitor.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    platforms='Linux'
)
