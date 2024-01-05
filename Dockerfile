# Python のベースイメージを使用
FROM python:3.11

# 作業ディレクトリの設定
WORKDIR /app

# 必要なPythonライブラリをインストールするための requirements.txt ファイルをコピー
COPY requirements.txt ./

# requirements.txt にリストされている依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# recv_event_hub.py をコンテナ内の作業ディレクトリにコピー
COPY recv_service_bus.py ./

# コンテナ起動時に Python スクリプトを実行
CMD [ "python", "./recv_service_bus.py" ]
