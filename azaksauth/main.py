"""
Author: Adrian Hynes 2020 <adrianhynes@gmail.com>
"""
import adal
from msrestazure.azure_active_directory import AdalAuthentication
from azure.mgmt.containerservice import ContainerServiceClient
import os
import sys
import yaml
import tempfile
import argparse
from azure.cli.command_modules.acs.custom import merge_kubernetes_configurations
from pathlib import Path
import logging
import logging.config

LOGGER = logging.getLogger(__name__)

def parse_args(args):
    LOGGER.info("Parsing Arguments")
    parser = argparse.ArgumentParser()
    parser.add_argument('--tenant', help='Tenant ID', required=True)
    parser.add_argument('--subscription', help='Subscription ID', required=True)
    parser.add_argument('--resource-group', help='Resource Group Name', required=True)
    parser.add_argument('--cluster-name', help='Cluster Name', required=True)
    parser.add_argument('--username', help='Tenant Username', required=True)
    parser.add_argument('--password', help='Password', required=True)
    parsed_args = parser.parse_args(args)

    return parsed_args


def main():

    args = parse_args(sys.argv[1:])

    authority_url = ('https://login.microsoftonline.com/' + args.tenant)
    context = adal.AuthenticationContext(
        authority_url, api_version=1.0,
        )

    LOGGER.info("Authenticating to AAD using ARM Resource and Default Client ID")

    #Create credentials object from our adal username and password flow. 
    credentials = AdalAuthentication(
        context.acquire_token_with_username_password,
        'https://management.azure.com/',
        args.username,
        args.password,
        '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
    )

    LOGGER.info("Getting Kubeconfig Skeleton")
    #Get the skeleton kubeconfig
    client = ContainerServiceClient(credentials, args.subscription)
    credentialResults = client.managed_clusters.list_cluster_user_credentials(args.resource_group, args.cluster_name)

    LOGGER.info("Write Kubeconfig Skeleton to temp file")
    #Write skeleton kubeconfig to temp file
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(credentialResults.kubeconfigs[0].value.decode(encoding='UTF-8'))
        additional_file.flush()
    finally:
        additional_file.close()

    LOGGER.info("Load Kubeconfig Skeleton to dict")
    #Open skeleton kubeconfig into a dict and extract server, client and context name
    with open(temp_path) as file:
        kconfig = yaml.load(file, Loader=yaml.FullLoader)
        apiServer = kconfig.get('users')[0].get('user').get('auth-provider').get('config').get('apiserver-id')
        clientId = kconfig.get('users')[0].get('user').get('auth-provider').get('config').get('client-id')
        contextName = kconfig.get('contexts')[0].get('name')

    os.remove(temp_path)

    LOGGER.info("Authenticate with client on behalf of user to API Server App")
    #Generate access token, refresh token, expiry details using client and server
    token = context.acquire_token_with_username_password(
        resource=apiServer,
        username=args.username,
        password=args.password,
        client_id=clientId)

    LOGGER.info("Subbing in User Identity details into Kubeconfig dict")
    #Sub in above into kubeconfig dict
    kconfig['users'][0]['user']['auth-provider']['config']['access-token']=token['accessToken']
    kconfig['users'][0]['user']['auth-provider']['config']['refresh-token']=token['refreshToken']
    kconfig['users'][0]['user']['auth-provider']['config']['expires-in']=str(token['expiresIn'])
    kconfig['users'][0]['user']['auth-provider']['config']['expires-on']=token['expiresOn']

    LOGGER.info("Write Kubeconfig dict to temp file")
    #Write kubeconfig dict to temp file
    fd1, temp_path1 = tempfile.mkstemp()
    with open(temp_path1, 'w') as file:
        documents = yaml.dump(kconfig, file)

    #Get default kubeconfig location
    kconfigPath = str(Path.home()) + os.sep + '.kube' + os.sep + 'config'

    LOGGER.info("Check if ddefault Kubeconfig exists")
    #Create empty kubeconfig and path if it doesn't exist
    if os.path.exists(kconfigPath) != True:
        os.makedirs(os.path.dirname(kconfigPath), exist_ok=True)
        with open(kconfigPath, "w") as f:
            f.write("")

    LOGGER.info("merge_kubernetes_configurations temp kubeconfig with default kuebconfig")
    #Reuse Azure's method to merge our new kubeconfig with the existing one
    merge_kubernetes_configurations(kconfigPath, temp_path1, True, contextName)


if __name__ == '__main__':

    logging.basicConfig(filename="azaksauth.log",
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    main()