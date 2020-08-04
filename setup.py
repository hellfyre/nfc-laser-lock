import setuptools

setuptools.setup(
    name="nfclock",
    version="0.1",
    author="Steffen Arntz, Matthias Uschok",
    author_email="dev@uschok.de",
    description="Simple tool to identify and authenticate cheap nfc-tags against a DB of known authorized keys.",
    url="https://github.com/hellfyre/nfclock",
    packages=setuptools.find_packages(),
    python_requires='>=3.8'
)
