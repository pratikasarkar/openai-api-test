import hvac
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import sys
import json
# import conjur
from conjur import Client



class snowflake_utils:
    def __init__(self, name):
        self.name = name
        
    def get_snowflake_db_details(config_block, sf_conn_name):
        """
            Function   : get_snowflake_db_details(config_block, sf_conn_name, logger)
            Purpose    : To Decrypt snowflake authentication details from Vault & Config
            Parameters : config_block  : Config dictionary object with the SF Credentials
                         sf_conn_name  : Snowflake Connection Name
            Returns    : rowcount value
            """
        config = config_block
        # try:
        CONJUR_URL = config[sf_conn_name]['conjur_url']
        CONJUR_ACCOUNT = config[sf_conn_name]['conjur_account']
        CONJUR_USERNAME = config[sf_conn_name]['conjur_username']
        CONJUR_API_KEY = config[sf_conn_name]['conjur_api_key']
        ROLE_ID_VARIABLE = config[sf_conn_name]['role_id_variable']
        SECRET_ID_VARIABLE = config[sf_conn_name]['secret_id_variable']

        conjur_client = Client(url=CONJUR_URL,
                        account=CONJUR_ACCOUNT,
                        login_id=CONJUR_USERNAME,
                        api_key=CONJUR_API_KEY)

        sf_secret_key_path = config[sf_conn_name]['sf_secret_key_path']
        sf_secret_pwd_path = config[sf_conn_name]['sf_secret_pwd_path']
        vault_url = config[sf_conn_name]['URL']
        vault_namespace = config[sf_conn_name]['namespace']
    ###
        #vault_token = config[sf_conn_name]['token']
        vault_role_id = conjur_client.get(ROLE_ID_VARIABLE).decode("utf-8")
        vault_secret_id = conjur_client.get(SECRET_ID_VARIABLE).decode("utf-8")
        vault_token = hvac.Client(url=vault_url,namespace=vault_namespace).auth.approle.login(role_id=vault_role_id, secret_id=vault_secret_id, mount_point='approle')['auth']['client_token']
        ###
        vault_key_file_path = config[sf_conn_name]['keyfilepath']

        sf_account = config[sf_conn_name]['account']
        sf_user = config[sf_conn_name]['user']
        sf_role = config[sf_conn_name]['role']
        sf_database = config[sf_conn_name]['DATABASE']
        sf_warehouse = config[sf_conn_name]['WAREHOUSE']
        sf_vware = config[sf_conn_name]['VWARE']
        sf_stage = config[sf_conn_name]['stagename']

        # except Exception as e:
        #     print(str(e))
        #     sys.exit(1)
        key_pwd = ''
        # try:
        auth_type = 'KEY'
        client = hvac.Client(url=vault_url, namespace=vault_namespace, token=vault_token)
        jsonval = client.read(sf_secret_key_path)
        value = json.dumps(jsonval["data"])
        data = json.loads(value)
        print("Decrypting snowflake secret key")
        mykey = (data['private_key'])
        SNOWSQL_PRIVATE_KEY_PASSPHRASE = (data['SNOWSQL_PRIVATE_KEY_PASSPHRASE'])
        fh = open(vault_key_file_path, "w")
        fh.writelines(mykey)
        fh.close()
        with open(vault_key_file_path, "rb") as key:
            p_key = serialization.load_pem_private_key(key.read(), password=SNOWSQL_PRIVATE_KEY_PASSPHRASE.encode(), backend=default_backend())

        key_pwd = p_key.private_bytes(encoding=serialization.Encoding.DER, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())
        print("Retrieved snowflake key successfully")
        # except Exception as e:
        #     print(e, exc_info=True)
        #     print("Error in Retrieving snowflake key, trying to get password...")
        #     try:
        #         auth_type = 'PASSWORD'
        #         client = hvac.Client(url=vault_url, namespace=vault_namespace, token=vault_token)
        #         jsonval = client.read(sf_secret_pwd_path)
        #         value = json.dumps(jsonval["data"])
        #         data = json.loads(value)
        #         print("Decrypting snowflake password")
        #         key_pwd = (data['passwd'])
        #         print("Retrieved snowflake password successfully")
        #     except Exception as e:
        #         print("Error in connecting to snowflake, Please check the credentials...")
        #         print(e, exc_info=True)
        #         sys.exit(1)

        return sf_account, sf_user, key_pwd, sf_role, sf_database, sf_warehouse, sf_vware, sf_stage, auth_type