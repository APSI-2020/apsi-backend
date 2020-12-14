#!/bin/bash
echo "Adding users..."
cat lecturers.json | jq -c '.[]' | xargs -d'\n' -I {} curl -X POST -H "Content-Type: application/json" --data {} http://localhost:8000/api/auth/register/

echo "Retrieving token for first user..."
user=$(cat lecturers.json| jq -c '.[0]')
token=$(curl -X POST -H 'Content-Type: application/json' --data "${user}" http://localhost:8000/api/auth/login/ | jq -rc '.access')

echo "Access token: Bearer" $token

echo "Adding places..."
cat places.json | jq -c '.[]' | xargs -d'\n' -I {} curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${token}" --data {} http://localhost:8000/api/places/

echo "Adding events..."
cat events.json | jq -c '.[]' | xargs -d'\n' -I {} curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${token}" --data {} http://localhost:8000/api/events/
