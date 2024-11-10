# swipe

prometheus APIを使用してPodがRunningになっていないもののYamlファイルを取得するプログラム．


1. プログラム内のprometheus urlにapiのURLを入力
2. プログラム内のtarget_cluster_contextに対象のクラスタを使用するように設定したkubectlのコンテキスト名を入力
3. python3 swipe.pyで実行できます．

yaml_dataフォルダを作成しておく必要があるかもしれません．
