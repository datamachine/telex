#!/usr/bin/env bash

THIS_DIR=$(cd $(dirname $0); pwd)
cd $THIS_DIR

update() {
  git pull
  git submodule update --init --recursive --remote
  install_packages
}

# Will install a virtualenv on THIS_DIR/.virtualenv
install_virtualenv() {
  if [ ! -d ".virtualenv" ]; then
    virtualenv -p python3 .virtualenv
  fi
}

install_packages() {
  . .virtualenv/bin/activate
  pip install -r requirements.txt
}

install() {
  git pull
  git submodule update --init --recursive --remote
  cd tg && ./configure --disable-liblua --enable-python && make
  RET=$?; if [ $RET -ne 0 ];
    then echo "Error. Exiting."; exit $RET;
  fi
  cd ..
  if [ ! -e "plugins.conf" ]; then
    cp plugins.conf.example plugins.conf
  fi
  install_virtualenv
  install_packages
}

if [ "$1" = "install" ]; then
  install
elif [ "$1" = "update" ]; then
  update
else
  if [ ! -f ./tg/telegram.h ]; then
    echo "tg not found"
    echo "Run $0 install"
    exit 1
  fi

  if [ ! -f ./tg/bin/telegram-cli ]; then
    echo "tg binary not found"
    echo "Run $0 install"
    exit 1
  fi

  PYTHONHOME="$THIS_DIR/.virtualenv" ./tg/bin/telegram-cli -k ./tg/tg-server.pub -Z ./runner.py -l 1 &
  while [[ -n $(jobs -p) ]]; do
      if [[ -e "reload" ]]; then
        rm -vf "reload"
        echo RELOADING BOT
        kill $(jobs -p)
        PYTHONHOME="$THIS_DIR/.virtualenv" ./tg/bin/telegram-cli -k ./tg/tg-server.pub -Z ./runner.py -l 1 &
      fi
      sleep 1
  done
  
fi
