import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='azarashi',
    version='0.7.0',
    description='QZSS DCR Decoder',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nbtk/azarashi',
    author='nbtk',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    packages=setuptools.find_packages(),
    install_requires=[],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'azarashi=azarashi.__main__:main',
        ],
    },
)
