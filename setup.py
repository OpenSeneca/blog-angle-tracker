from setuptools import setup

setup(
    name="squad-blog-angle-tracker",
    version="1.0.0",
    description="Track and manage blog post ideas from content digest",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="OpenSeneca",
    url="https://github.com/OpenSeneca/squad-blog-angle-tracker",
    py_modules=["main"],
    install_requires=[
        # No external dependencies - uses only Python stdlib
    ],
    entry_points={
        "console_scripts": [
            "blog-angle-tracker=main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
