FROM ubuntu:18.04
ARG USER_NAME
ARG USER_ID
ARG TRADER_PATH=/Projects/trading-bot/
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive


# apt-packages
RUN sed -i "s/archive.ubuntu/mirror.kakao/g" /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y software-properties-common \
 && add-apt-repository -y ppa:neovim-ppa/stable \
 && add-apt-repository -y ppa:deadsnakes/ppa \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates git gcc g++ curl wget sudo pkg-config xorg tzdata \
	python3.9 python3.9-distutils \
    locales iputils-ping net-tools tree \
    ssh openssh-server \
    neovim tmux screen \
 && curl -sL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh \
 && bash nodesource_setup.sh \
 && apt-get install -y nodejs build-essential checkinstall \
 && apt-get clean \
 && rm -r /var/lib/apt/lists

# pip-packages
#WORKDIR /
RUN ln -sf /usr/bin/python3.9 /usr/bin/python \
 && ln -sf /usr/bin/python3.9 /usr/bin/python3 \
 && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
 && python3.9 get-pip.py \
 && rm get-pip.py \
 && python3.9 -m pip install --upgrade pip \
 && python3.9 -m pip install cython wheel setuptools cmake \
 && python3.9 -m pip install numpy pandas Pyx \
 && python3.9 -m pip install pyupbit ccxt \
 && python3.9 -m pip install lxml tabulate PyYAML==5.4.1 \
 && python3.9 -m pip install opencv-python \
 && python3.9 -m pip cache purge

RUN npm install -g yarn

# localtime
RUN locale-gen "en_US.UTF-8"
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

# vim-plug
RUN sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'

# create user
RUN useradd --create-home --shell /bin/bash --uid ${USER_ID} ${USER_NAME} \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && usermod -aG sudo ${USER_NAME}
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}
RUN touch /home/${USER_NAME}/.Xauthorityi \
 && mkdir -p /home/${USER_NAME}/.config/nvim/ \
 && touch /home/${USER_NAME}/.config/nvim/init.vim
