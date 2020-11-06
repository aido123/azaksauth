# AZ AKS Auth

![version-image][version-image]

Authenticate NON Interactively to AKS Clusters

## Sample

azaksauth --tenant "9b411214-6cd9-4672-9034-b55bf7d44b12" --username "clusteruser@mytenant.onmicrosoft.com" --password "hard2Guess" --subscription "a1234b5c-1234-5678-abcd-1234abcded12" --resource-group "adrian-group" --cluster-name "adriancluster"

## Installation

### Prerequisites
* Python3
* PIP3

### Running Instructions

1. Install the pip module into your python library.

   pip install azaksauth/

2. Export your PATH env to pick up the alias wiki when running the python module form your machine

   export PATH=~/.local/bin:$PATH

3. Run the azaksauth command

   azaksauth --tenant "9b411214-6cd9-4672-9034-b55bf7d44b12" --username "clusteruser@mytenant.onmicrosoft.com" --password "hard2Guess" --subscription "a1234b5c-1234-5678-abcd-1234abcded12" --resource-group "adrian-group" --cluster-name "adriancluster"

OR

1. Run the python module command. Navigate into wordfrequency and Run.

   python -m azaksauth.main --tenant "9b411214-6cd9-4672-9034-b55bf7d44b12" --username "clusteruser@mytenant.onmicrosoft.com" --password "hard2Guess" --subscription "a1234b5c-1234-5678-abcd-1234abcded12" --resource-group "adrian-group" --cluster-name "adriancluster"

## Uninstall

pip uninstall azaksauth

### Parameters

*tenant* - tenant id

*subscription* - subscription id

*resource-group* - resource group name

*cluster-name* - cluster name

*username* - tenant username

*password* - password


[version-image]: https://img.shields.io/badge/version-0.0.1-green.svg?style=plastic
