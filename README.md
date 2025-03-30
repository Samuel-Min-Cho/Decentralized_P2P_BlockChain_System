docker-compose -f docker-compose.postgres.yml up -d

docker-compose -f docker-compose.kafka.yml up -d

python server.py


curl -X POST http://localhost:8000/transaction \
  -H "Content-Type: application/json" \
  -d '{"sender": "UserA", "recipient": "UserB", "amount": 25}'


docker-compose up --build

docker-compose build server

docker-compose up


docker buildx build --platform linux/amd64 -t finalprojecct.azurecr.io/backend-image:latest . --push 