# Telex
A Telegram Bot based on plugins. 

This bot uses tg and tgl C libraries for its bindings, and we have been contributing our python bindings as we work through it.

Everything is being written for Python 3.4 currently. Everything works in a virtualenv installed and sourced in the launch script.


There are not a ton of useful plugins by default, but you can run ``` !pkg update ``` and then ``` !pkg list all ``` to see what plugins are available to install.

Some plugins require admin permissions. You can set an admin in permissions.conf using the following format

```
[groups]
  admins = <userid#>,<userid#>,<userid#>
```

You can get your user id number by sending the following query to the bot

```
!tginfo id
```

### Installation
Steps:
1: Clone git repository.
2: Install dependencies
3: Install telex
4: Setup tg
5: Run telex

#### Cloning the repository

    git clone --recursive https://github.com/datamachine/telex.git && cd telex

#### Installing dependencies

##### Linux and BSDs

Install libs: readline, openssl and (if you want to use config) libconfig, liblua, python3-dev, python-virtualenv and libjansson.

Note: Installation was tested only on Ubuntu and Debian

###### On Ubuntu/Debian use: 

    sudo apt-get install libreadline-dev libconfig-dev libssl-dev lua5.2 liblua5.2-dev libevent-dev libjansson-dev python3-dev python-virtualenv make 

###### On gentoo:

    sudo emerge -av sys-libs/readline dev-libs/libconfig dev-libs/openssl dev-lang/lua dev-libs/libevent dev-libs/jansson dev-lang/python-3 dev-python/virtualenv 

###### On Fedora:

    sudo yum install lua-devel openssl-devel libconfig-devel readline-devel libevent-devel libjansson-devel python3-devel python-virtualenv 

###### On FreeBSD:

    pkg install libconfig libexecinfo lua52 python3 devel/py-virtualenv

#### Installing telex
To install the bot, run the following in telex directory.

    ./launch.sh install

#### Setting up Telegram cli (verifying phone number)
Do the following.

    cd tg
    bin/telegram-cli -k tg-server.pub

It will ask for your phone number and confirmation code.
After successful verificaion of phone number, press Ctrl+C to stop telegram-cli.

#### Running telex

To start the bot, run the following in telex directory.

    ./launch

### Running telex as a service

#### For systems with systemd

If you have [systemd](http://www.freedesktop.org/wiki/Software/systemd/), you can run the bot as a service by following the below procedure.

To check if you have systemd, run 

    if test -d /usr/lib/systemd; then echo "exist"; else echo "doesn't exist"; fi

If output is ```exist``` then you have systemd and you can continue with below steps.

Edit the config file:

    sed -i "s/<username>/$(whoami)/g" temp/telex.service
    sed -i "s/<telexpath>/$(pwd)/g" temp/telex.service
    sudo cp temp/telex.service /etc/systemd/system/

Enabling service:

    sudo systemctl enable telex.service

Starting/Stopping telex:

    sudo systemctl start telex.service # To start it
    sudo systemctl status telex.service # To check status
    sudo systemctl stop telex.service # To stop it

Make sure that the status is Active: active (running)

#### For systems with upstart

If you have [upstart](http://upstart.ubuntu.com/), you can run the bot as a service by following the below procedure.

To check if you have upstart, run 

    if test -d /usr/lib/upstart; then echo "exist"; else echo "doesn't exist"; fi

If output is ```exist``` then you have upstart and you can continue with below steps.

Edit the config file:

    sed -i "s/<username>/$(whoami)/g" temp/telex.conf
    sed -i "s/<telexpath>/$(pwd)/g" temp/telex.conf
    sudo cp temp/telex.conf /etc/init/

Starting/Stopping telex:

    sudo start telex # To start it
    sudo stop telex # To stop it

#### For Mac
 Follow insrucions here: http://superuser.com/questions/264954/can-i-use-a-bash-script-as-a-service-in-os-x-without-having-to-set-it-up-trough

# Notes
While already very capable, this bot is still in relatively early development. Some plugin names, or plugin API calls may be modifed. However, we are starting to settle on our stable APIs.

With that said, we do strive to have the bot continue to function seemlessly when pulling the latest HEAD

# Contact

The primary developers are Vince (@Surye) and Phillip (@Tyrannosaurus) and can be contacted directly through telegram.

You can also join our telegram group using the link: https://telegram.me/joinchat/05c5c2f60112fa104d1c0c563b2fd34a

Bug reports and issues can be reported at: https://github.com/datamachine/telex/issues

# Known Issues

## Not recieving telegram verification text on initial launch

Try running tg directly.

```
$ tg/bin/telegram-cli -k tg-server.pub
```

Once you verify the client, you can stop it and run the launch.sh script again.

