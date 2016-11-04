from setuptools import setup


setup(
    name='Munibot',
    version='0.0.1',
    description='A Slack bot to inform Plethorans of the Muni KT train',
    author='Jayme Woogerd & Kairui Wang',
    author_email='jayme@plethora.com',
    url='https://github.com/jwoogerd/munibot',
    py_modules=[],
    scripts=['munibot'],
    zip_safe=False,
    install_requires=[
        'requests',
    ],
)
