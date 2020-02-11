from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="richcontext-scholapi",
    version="1.1.1",
    author="Coleridge Initiative",
    author_email="dataanalytics@coleridgeinitiative.org",
    description="Rich Context API integrations for federating discovery services and metadata exchange across multiple scholarly infrastructure providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Coleridge-Initiative/RCApi",
    packages=find_namespace_packages(include=['richcontext.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.5",
    install_requires=[
        "beautifulsoup4",
        "biopython",
        "crossref-commons",
        "dimcli",
        "requests",
        "requests-cache",
        "selenium",
        "xmltodict",
    ],
    keywords="Rich Context, DOI, ISSN, ROR, ORCID, PubMed, EuropePMC, Scholix, Crossref, DataCide, OpenAIRE, Unpaywall, dissemin, Semantic Scholar, RePEc, Dimensions, discovery, discovery service, federated API, federated metadata, knowledge graph, metadata API, metadata exchange, metadata, persistent identifiers, research publication ontology, research publications, scholarly infrastructure, scholarly metadata, scholarly publishing",
    license="MIT",
    include_package_data=True,
    zip_safe=False
)
