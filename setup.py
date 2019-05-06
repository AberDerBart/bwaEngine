import setuptools

setuptools.setup(
    name="junebugEngine",
    version="1.0.0",
    author="Nils Kornfeld, Jonas Grosse-Holz",
    author_email="aber@der-b.art",
    description="A platformer game engine",
    packages=setuptools.find_packages(),
    python_requires='>=3.7,<4',
    install_requires=[
       'pygame'
    ]
)
