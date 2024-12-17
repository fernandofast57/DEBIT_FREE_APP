
from setuptools import setup, find_packages

setup(
    name="gold-investment-backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Quart==0.19.4',
        'Werkzeug>=3.0.0',
        'Flask-SQLAlchemy==3.1.1',
        'Flask-Migrate==4.0.5',
        'pytest-asyncio==0.23.3',
        'SQLAlchemy==2.0.21',
        'Flask-Cors==5.0.0',
        'Flask-Login==0.6.3',
        'python-dotenv==1.0.0',
        'web3==6.8.0',
        'eth-account==0.8.0',
        'eth-typing==3.4.0',
        'eth-utils==2.2.0',
        'hexbytes==0.3.1'
    ],
    python_requires='>=3.11',
)
