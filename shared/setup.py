from setuptools import setup

setup(
    name="shared",
    version="1.0.0",
    package_dir={"shared": "."},
    packages=["shared", "shared.models", "shared.utils"],
    install_requires=[
        "pydantic>=2.6.0",
        "firebase-admin>=6.5.0",
        "google-generativeai>=0.4.0"
    ]
)
