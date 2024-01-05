# 利用方法

## 環境変数の宣言

.env ファイルの内容を適宜書き換え、読み込みます
```bash
source .env
```

## リソースグループの作成

```bash
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
```

## Service Busの構築

```bash
export SERVICE_BUS_NAMESPACE=ksservicebus2024
export SERVICE_BUS_QUEUE_NAME=kssbqueue
az servicebus namespace create --resource-group $RESOURCE_GROUP --name $SERVICE_BUS_NAMESPACE --location $LOCATION
az servicebus queue create --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE --name $SERVICE_BUS_QUEUE_NAME
```

接続文字列の取得

```bash
export SERVICE_BUS_CONNECTION_STR=`az servicebus namespace authorization-rule keys list --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE --name RootManageSharedAccessKey --query primaryConnectionString --output tsv`
```

# Dockerイメージの作成と登録

```bash
docker build -t event_app .
```

(Optional) ローカルでの起動

```bash
docker run -e SERVICE_BUS_CONNECTION_STR=$SERVICE_BUS_CONNECTION_STR -e SERVICE_BUS_QUEUE_NAME=$SERVICE_BUS_QUEUE_NAME event_app
```

ACRの作成とイメージの登録

```bash
az acr create \
    --name "$CONTAINER_REGISTRY_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Basic \
    --admin-enabled true

docker tag event_app $CONTAINER_REGISTRY_NAME.azurecr.io/event_app:latest
az acr login --name $CONTAINER_REGISTRY_NAME
docker push $CONTAINER_REGISTRY_NAME.azurecr.io/event_app:latest
```

コンテナアプリ環境作成とコンテナジョブの登録

```bash
az containerapp env create --name $ENVIRONMENT --resource-group $RESOURCE_GROUP --location $LOCATION

JOB_NAME=aca-event-test-job-service-bus

az containerapp job create \
    --name "$JOB_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --env-vars "SERVICE_BUS_CONNECTION_STR=$SERVICE_BUS_CONNECTION_STR" "SERVICE_BUS_QUEUE_NAME=$SERVICE_BUS_QUEUE_NAME" \
    --environment "$ENVIRONMENT" \
    --trigger-type "Event" \
    --replica-timeout "1800" \
    --replica-retry-limit "1" \
    --replica-completion-count "1" \
    --parallelism "1" \
    --min-executions "0" \
    --max-executions "2" \
    --polling-interval "60" \
    --image "$CONTAINER_REGISTRY_NAME.azurecr.io/event_app" \
    --cpu "0.5" \
    --memory "1Gi" \
    --registry-server "$CONTAINER_REGISTRY_NAME.azurecr.io" \
    --secrets "connection-string-secret=$SERVICE_BUS_CONNECTION_STR" \
    --scale-rule-name "servicebus" \
    --scale-rule-type "azure-servicebus" \
    --scale-rule-metadata "queueName=$SERVICE_BUS_QUEUE_NAME" "namespace=$SERVICE_BUS_NAMESPACE"\
    --scale-rule-auth "connection=connection-string-secret"
```

## 動作確認

```bash
python send_service_bus.py
```
でメッセージを送信します。正常に動作していればコンテナアプリインスタンスが起動します。