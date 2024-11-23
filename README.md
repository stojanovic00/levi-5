terraform apply
terraform output -raw private_key_pem > id_rsa
# SSH INTO EC2
ssh -i id_rsa ubuntu@3.120.173.191


## Connect to DocDB:


mongo --ssl --host docdb-cluster.cluster-c12o0ge4cwh8.eu-central-1.docdb.amazonaws.com:27017 \
  --sslCAFile rds-combined-ca-bundle.pem \
  --username docdb_user \
  --password 'YourSecurePassword123!'



mongosh --ssl --host docdb-instance.c12o0ge4cwh8.eu-central-1.docdb.amazonaws.com:27017 --sslCAFile rds-combined-ca-bundle.pem --username docdb_user --password 'YourSecurePassword123!' 



api_endpoint = "https://alnrssw7e3.execute-api.eu-central-1.amazonaws.com/prod/path"
docdb_cluster_endpoint = "docdb-cluster.cluster-c12o0ge4cwh8.eu-central-1.docdb.amazonaws.com"
ec2_public_ip = "3.120.173.191"
lambda_api_url = "https://ykmiu45e43.execute-api.eu-central-1.amazonaws.com/prod"
private_key_pem = <sensitive>


scp -i id_rsa -r codebase ubuntu@3.120.173.191:/home/ubuntu/flask_app