import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8s_service",
    version="0.0.1",
    author="Dominik Fleischmann",
    author_email="dominik.fleischmann@canonical.com",
    description="K8s Service Operator Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["k8s_service"],
    install_requires=[
        "ops",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
