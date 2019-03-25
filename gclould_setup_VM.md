## Creating the SSH keys
* ssh-keygen -t rsa -f ~/.ssh/[KEY_FILENAME] -C [USERNAME]
* download the public key and upload that to Metadata -> sshkeys
* Then, ssh -i [Path to private key] localhost

## Setting up gcloud API
* gcloud auth application-default login


