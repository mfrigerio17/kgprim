import setuptools
import os, glob, shutil

with open("readme.md", "r") as fh:
    long_description = fh.read()


class RealClean(setuptools.Command):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './build ./dist ./*.egg-info src/*.egg-info'.split(' ')

    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        for path_spec in RealClean.CLEAN_FILES:
            for path in glob.glob(path_spec):#[str(p) for p in abs_paths]:
                print('removing {0}'.format(path))
                shutil.rmtree(path)

pkgs = setuptools.find_packages(where='src')
pkgs.extend( setuptools.find_namespace_packages(where='src', include=['kgprim.ct.*']) )

setuptools.setup(
    name="kgprim",
    version="0.1.0",
    author="Marco Frigerio",
    author_email="marco.frigerio@kuleuven.be",
    description="Kinematics/geometric primitives",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages = pkgs,

    # tell distutils packages are under src/ - Do not ask me why this is
    # required in addition to the previous option.
    package_dir = {'': 'src'},

    package_data = {
        # include the textX grammar
        "motiondsl": ["*.tx"],
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.3',
    
    install_requires = [
        'networkx',
        'numpy',
        'sympy',
        'textX'
    ],

    cmdclass={
        'realclean': RealClean,
    },
)



