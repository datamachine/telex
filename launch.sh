#!/usr/bin/env bash

THIS_DIR=$(cd $(dirname $0); pwd)
cd $THIS_DIR

update() {
  git pull
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
  . .virtualenv/bin/activate
  python3 ./runner.py &
  while [[ -n $(jobs -p) ]]; do
      if [[ -e "reload" ]]; then
        rm -vf "reload"
        echo RELOADING BOT
        kill $(jobs -p)
        python3 ./runner.py &
      fi
      sleep 1
  done
  
fi
