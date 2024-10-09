# swipe

prometheus APIを使用してPodがRunningになっていないもののYamlファイルを取得するプログラム．

今後，別クラスタでそのYamlを適用して確認できるようにします．
最終的にはコンテナにしたい．

プログラム内のprometheus urlにapiのURLを入力して，python3 swipe.pyで実行できます．
yaml_dataフォルダを作成しておく必要があるかもしれません．
