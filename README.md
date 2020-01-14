# linux configuration for udactiy nanodegree #

## Description ##
- ip : 3.11.122.244
- url : 3.11.122.244.xip.io *For oauth to work proberly*
- ssh: 2200
- user : grader 
- access through remote ssh : ssh -i private_key.pem grader@3.11.122.244
- passphrase: grader
- grader password : grader


## Packages installed ##
- sqlalchmey
- flask
- httplib2
- oauth2client

## Software installed ##
- apache2
- postgresql
- python-psycopg

## Steps ##
- Create new user grader **can run commands using sudo**
- disable root remote access from sshd_configfile
- ssh not on default port (2200)
- Allow connections only for ports (2200, 80, 123)
- Users must use rsa to authenticate
- all packages up to date
- Database configure for postgresql with database catalog 
- Configure web server to work with wsgi 

## References ##
- [a link](https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/)
- [a Link](https://github.com/jungleBadger/-nanodegree-linux-server?fbclid=IwAR0dzOUvYtrIhP3_TPnU3lcTrQ_R64Y4hmoXiBo-9vhjTn-r00ppZnceois)
