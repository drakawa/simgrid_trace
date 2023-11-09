# simgrid_trace

## 前提
- docker, docker-composeが実行可能である

## Dokcerのbuild

- コマンド
```
docker-compose up --build -d
```

- 実行結果
```
[~/work/simgrid_trace]
$ docker-compose up --build -d
Building test
[+] Building 164.2s (15/16)                                                                                                                                                                       docker:default
[+] Building 165.1s (16/16) FINISHED                                                                                                                                                              docker:default
 => [internal] load .dockerignore                                                                                                                                                                           0.0s
 => => transferring context: 2B                                                                                                                                                                             0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                                        0.0s
 => => transferring dockerfile: 594B                                                                                                                                                                        0.0s
 => [internal] load metadata for docker.io/library/ubuntu:18.04                                                                                                                                             0.8s
 => CACHED [ 1/11] FROM docker.io/library/ubuntu:18.04@sha256:152dc042452c496007f07ca9127571cb9c29697f42acbfad72324b2bb2e43c98                                                                              0.0s
 => [internal] load build context                                                                                                                                                                           0.1s
 => => transferring context: 210.57kB                                                                                                                                                                       0.1s
 => [ 2/11] RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install --no-install-recommends g++ clang python3 cmake libboost-dev libboost-context-dev doxygen gfortran make per  80.4s
 => [ 3/11] RUN pip3 install networkx                                                                                                                                                                       1.9s
 => [ 4/11] RUN mkdir /root/simgrid_inst                                                                                                                                                                    0.5s
 => [ 5/11] RUN mkdir /root/simgrid_inst/simgrid-v3.18                                                                                                                                                      0.4s
 => [ 6/11] WORKDIR /root/simgrid_inst/simgrid-v3.18                                                                                                                                                        0.1s
 => [ 7/11] COPY ./simgrid-v3.18/ /root/simgrid_inst/simgrid-v3.18/                                                                                                                                         0.2s
 => [ 8/11] RUN cmake -DCMAKE_INSTALL_PREFIX=/opt/simgrid .                                                                                                                                                 4.7s
 => [ 9/11] RUN make -j8                                                                                                                                                                                   64.9s
 => [10/11] RUN make install                                                                                                                                                                                5.5s
 => [11/11] WORKDIR /root/workspace                                                                                                                                                                         0.1s
 => exporting to image                                                                                                                                                                                      5.3s
 => => exporting layers                                                                                                                                                                                     5.3s
 => => writing image sha256:79745b5766eda5100154a4780be4e2b1d73dd36ddd2eb91229e7a2b8e6cad6ad                                                                                                                0.0s
 => => naming to docker.io/library/simgrid_trace_test                                                                                                                                                       0.0s
Creating simgrid_trace_test_1 ... done
```

- ./docker-compose, ./Dockerfile
  - docker-compose.ymlでコンテナ名をtestとし、カレントディレクトリを見れるようにしている
  - Dockerfile内でUbuntu18.04をビルドし、以下を実行している
    - 必要パッケージ取得
    - pythonのライブラリ (networkx) 取得
    - simgridのインストール
   
