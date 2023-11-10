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
    - python3のライブラリ (networkx) 取得
    - simgrid3.18のインストール
  
## Nas Parallel Benchmarks 3.3 (NPB3.3-MPI) のmake
- コンテナ内のシェルへの接続コマンド
```
docker-compose exec test /bin/bash
```

以下、コンテナ内のシェルでの作業

- コマンド
```
cd ~/workspace/NPB3.3-MPI/
make suite
```

- 実行結果
```
root@99993cd033e9:~# cd ~/workspace/NPB3.3-MPI/
root@99993cd033e9:~/workspace/NPB3.3-MPI# make suite
make[1]: Entering directory '/root/workspace/NPB3.3-MPI/FT'
rm -f *.o *~ mputil*
rm -f ft npbparams.h core
...
```

 - binに各ベンチマークの実行プログラムが生成される
```
root@99993cd033e9:~/workspace/NPB3.3-MPI# ls bin/
bt.W.64  cg.W.64  dt.W.x  ep.W.64  ft.W.64  is.W.64  lu.W.64  mg.W.64  sp.W.64
```

- config/make.def, config/suite.def
  - make.def内で、コンパイラ等にsimgridのものを指定し、simgridでMPI実行可能なプログラムを生成している
  - suite.def内でベンチマーク種類・問題サイズ・プロセス数 (例: bt.W.64) を指定している
    - 行を追加して実行プログラムを追加生成可能
    - 以降、dtを除くアプリケーションについて、サイズW, プロセス数64のものを評価対象とする

## platform (.xml), hostfile (.txt) ファイルの生成
- smpirunに入力するplatform (計算ノードの帯域、ネットワーク上の各リンクの帯域・遅延）、hostfile (計算ノードとルータの接続関係) ファイルを生成
  
- コマンド
```
cd ~/workspace/NPB3.3-MPI/
python3 xmlgen_crossbar.py 64
```

- 実行結果
```
root@99993cd033e9:~/workspace/NPB3.3-MPI# python3 xmlgen_crossbar.py 64
edgelist: []
nodelist: [1]
# of routers: 1
output node-router list: simgrid_topo/crossbar_64.txt
output xmlfile: simgrid_topo/crossbar_64.xml
```

- 生成されるplatformでは、64ポートの1個のルータに64個の計算ノードが接続されている
  - これはネットワーク評価としては正しい設定ではないが、プロセス間の通信トレースを取得するためネットワークを抽象化している
  - simgrid上でルータ間ネットワークを設定しシミュレーションすることも可能だが、シミュレーション時間が膨大となる

## smpirunの実行 (ログファイル, 通信トレースのcsvファイルの取得)

### 単一シミュレーション実行

例: is.W.64

- コマンド
```
cd ~/workspace/NPB3.3-MPI/
python3 smpirun_eval.py crossbar_64 is W
```

- 実行結果
```
root@99993cd033e9:~/workspace/NPB3.3-MPI# python3 smpirun_eval.py crossbar_64 is W
./simgrid_topo/crossbar_64.txt
True
./simgrid_topo/crossbar_64.xml
True
./bin/is.W.64
True
smpirun --cfg=smpi/privatize_global_variables:yes -platform ./simgrid_topo/crossbar_64.xml -hostfile ./simgrid_topo/crossbar_64.txt ./bin/is.W.64 --log=chaix.threshold:verbose --log=chaix.fmt:%m%n --log=chaix.app:splitfile:1000000000:./simgrid_topo//crossbar_64_is.W.64_trace_%.csv
['smpirun', '--cfg=smpi/privatize_global_variables:yes', '-platform', './simgrid_topo/crossbar_64.xml', '-hostfile', './simgrid_topo/crossbar_64.txt', './bin/is.W.64', '--log=chaix.threshold:verbose', '--log=chaix.fmt:%m%n', '--log=chaix.app:splitfile:1000000000:./simgrid_topo//crossbar_64_is.W.64_trace_%.csv']
[0.000000] [xbt_cfg/INFO] Configuration change: Set 'surf/precision' to '1e-9'
[0.000000] [xbt_cfg/INFO] Configuration change: Set 'network/model' to 'SMPI'
[0.000000] [xbt_cfg/INFO] Configuration change: Set 'smpi/privatize_global_variables' to 'yes'
[0.000000] [xbt_cfg/INFO] Option smpi/privatize_global_variables has been renamed to smpi/privatization. Consider switching.
[0.000000] [surf_parse/INFO] You're using a v4.0 XML file (./simgrid_topo/crossbar_64.xml) while the current standard is v4.1 That's fine, the new version is backward compatible.

...

[0.000000] /root/simgrid_inst/simgrid-v3.18/src/surf/xml/surfxml_sax_cb.cpp:197: [surf_parse/WARNING] Deprecated unit-less value '1.0e-07' for latency of link ls1. Append 's' to your time to get seconds
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective gather
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective allgather
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective allgatherv
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective allreduce
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective alltoall
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective alltoallv
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective reduce
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective reduce_scatter
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective scatter
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective bcast
[0.000000] [smpi_coll/INFO] Switch to algorithm mvapich2 for collective barrier
[0.005000] [smpi_kernel/INFO] Simulated time: 0.00500008 seconds.

The simulation took 0.676308 seconds (after parsing and platform setup)
0.165726 seconds were actual computation of the application
```

- simgrid_topo内に、ログファイル (crossbar_64_is.W.64.log), 通信トレースのcsvファイル (crossbar_64_is.W.64_trace_0.csv) が保存される
  - logファイル内のMop/s を性能評価結果として利用することが多い
  - csvファイルに計算ノード間の通信トレース（src,dst,size,rate,start,latency,route）が記録される
- 実態としては以下のコマンドを実行している
```
smpirun --cfg=smpi/privatize_global_variables:yes -platform ./simgrid_topo/crossbar_64.xml -hostfile ./simgrid_topo/crossbar_64.txt ./bin/is.W.64 --log=chaix.threshold:verbose --log=chaix.fmt:%m%n --log=chaix.app:splitfile:1000000000:./simgrid_topo//crossbar_64_is.W.64_trace_%.csv
```

 ### シミュレーションの一括実行
 - コマンド
```
python3 smpirun_evalall.py
```

- 各アプリケーションのログファイル、通信トレースのcsvファイルが得られる
```
root@f10372aaa07f:~/workspace/NPB3.3-MPI# ls simgrid_topo/*.log
simgrid_topo/crossbar_64_bt.W.64.log  simgrid_topo/crossbar_64_ep.W.64.log  simgrid_topo/crossbar_64_is.W.64.log  simgrid_topo/crossbar_64_mg.W.64.log
simgrid_topo/crossbar_64_cg.W.64.log  simgrid_topo/crossbar_64_ft.W.64.log  simgrid_topo/crossbar_64_lu.W.64.log  simgrid_topo/crossbar_64_sp.W.64.log
root@f10372aaa07f:~/workspace/NPB3.3-MPI# ls simgrid_topo/*.csv
simgrid_topo/crossbar_64_bt.W.64_trace_0.csv  simgrid_topo/crossbar_64_ep.W.64_trace_0.csv  simgrid_topo/crossbar_64_is.W.64_trace_0.csv  simgrid_topo/crossbar_64_mg.W.64_trace_0.csv
simgrid_topo/crossbar_64_cg.W.64_trace_0.csv  simgrid_topo/crossbar_64_ft.W.64_trace_0.csv  simgrid_topo/crossbar_64_lu.W.64_trace_0.csv  simgrid_topo/crossbar_64_sp.W.64_trace_0.csv
```


