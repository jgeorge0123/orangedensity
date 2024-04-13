from setuptools import setup

setup(
    name="Density",
    packages=["orangedensity"],
    package_data={"orangedensity": ["icons/*.svg"]},
    classifiers=["Example :: Invalid"],
    # Declare orangedemo package to contain widgets for the "Demo" category
    entry_points={"orange.widgets": "Density = orangedensity"},
)