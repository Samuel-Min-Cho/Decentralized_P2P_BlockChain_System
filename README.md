docker-compose -f docker-compose.postgres.yml up -d

docker-compose -f docker-compose.kafka.yml up -d

python server.py


curl -X POST http://48.217.128.193/transaction \
  -H "Content-Type: application/json" \
  -d '{"sender": "UserA", "recipient": "UserB", "amount": 25}'

curl http://135.234.248.94/docs


docker-compose up --build

docker-compose build server

docker-compose up


docker buildx build -f Dockerfile.server --platform linux/amd64 -t coe892finalmc.azurecr.io/backend-fastapi-image:latest . --push 

docker buildx build -f Dockerfile.node --platform linux/amd64 -t coe892finalmc.azurecr.io/backend-node-image:latest . --push 

docker buildx build -f Dockerfile --platform linux/amd64 -t coe892finalmc.azurecr.io/frontend-image:latest . --push 

az aks get-credentials --resource-group 892FinalProject --name finalprojectbackend

az aks create \
  --resource-group 892FinalProject \
  --name finalprojectbackend \
  --location eastus \
  --node-count 2 \
  --generate-ssh-keys

kubectl apply -f .

kubectl delete all --all

kubectl apply -f kubernet.yaml

kubectl logs 
  describe pod 

kubectl get pods

kubectl get svc


kubectl get svc fastapi

az webapp update \
  --name 892FinalFrontEnd \
  --resource-group 892FinalProject \
  --set httpsOnly=false
