
from setuptools import setup, find_packages

setup(
    name="gold-investment-backend",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.0.1',
        'Flask-SQLAlchemy>=2.5.1',
        'Flask-Migrate>=3.1.0',
        'web3>=6.0.0',
        'pytest>=7.3.1',
        'pytest-asyncio>=0.21.0',
    ]
)
