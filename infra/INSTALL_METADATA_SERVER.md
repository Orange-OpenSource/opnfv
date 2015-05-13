# Set and configure the Metadata server for OpenSteak

## Add IP 169.254.169.254 to your admin network interface

```ip a a 169.254.169.254/32 dev eth0```

or do it in your network config file

## Change default foreman apache config

Edit __/etc/apache2/sites-available/05-foreman.conf__

After

```
  ## Server aliases
  ServerAlias foreman
```

Add

```
<Location /2009-04-04 >
  ProxyPass http://127.0.0.1:8888/2009-04-04
</Location>
<Location /latest >
  ProxyPass http://127.0.0.1:8888/latest
</Location>

```

## Install deps for python libs

```
sudo aptitude install python3-pip python3-tornado
sudo pip3 install beautifulsoup4 PyYAML requests requests-futures
```

## Run the server

With foreman login/password:

```/home/ubuntu/opnfv/infra# python3 metadata-server.py admin password```
