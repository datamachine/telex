# telegram-pybot
A Telegram Bot based on plugins. 

This bot uses tg and tgl C libraries for its bindings, and we have been contributing our python bindings as we work through it.

Everything is being written for Python 3.4 currently. Everything works in a virtualenv installed and sourced in the launch script.

    git clone https://github.com/datamachine/telegram-pybot --recursive
    cd telegram-pybot
    ./launch.sh install
    ./launch.sh

There are not a ton of useful plugins by default, but you can run ``` !pkg update ``` and then ``` !pkg list all ``` to see what plugins are available to install.

# Notes
While already very capable, this bot is still in relatively early development. Some plugin names, or plugin API calls may be modifed. However, we are starting to settle on our stable APIs.

With that said, we do strive to have the bot continue to function seemlessly when pulling the latest HEAD

# Contact

The primary developers are Vince (@Surye) and Phillip (@Tyrannosaurus) and can be contacted directly through telegram.

You can also join our telegram group using the link: https://telegram.me/joinchat/05c5c2f60112fa104d1c0c563b2fd34a

Bug reports and issues can be reported at: https://github.com/datamachine/telegram-pybot/issues

# Known Issues

## Not recieving telegram verification text on initial launch

Try running tg directly.

```
$ tg/bin/telegram-cli
```

Once you verify the client, you can stop it and run the launch.sh script again.

