# Usage: pass in the kafka pod ID as the argument

kubectl exec -i $1 -- bash -c 'kafka-topics.sh --create --replication-factor 1 --partitions 1 --topic locations --zookeeper $ZOO1_SERVICE_HOST'
echo "\nListing all topics:"
kubectl exec -i $1 -- bash -c 'kafka-topics.sh --zookeeper $ZOO1_SERVICE_HOST --list'