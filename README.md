# Blockchain Training

## Initial setup

Execute the following command in the project root.

```Shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Start the node.

```Shell
PORT=8080 python3 src/blockchain.py
```

Mine the block.

```Shell
curl -X GET 'http://localhost:8080/mine'
```

Send transaction.

```Shell
curl -X POST -H "Content-type: application/json" -d '{"sender":"i5irin","recipient":"you","amount":5}' 'http://localhost:8080/transactions/new'
```

Check the chain.

```Shell
curl -X GET 'http://localhost:8080/chain'
```

Register another node.

```Shell
PORT=8081 python3 src/blockchain.py
curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["http://localhost:8081"]}' "http://localhost:8080/nodes/register"
```

Mine more blocks on new nodes.

```Shell
curl -X GET 'http://localhost:8081/mine'
curl -X GET 'http://localhost:8081/mine'
curl -X GET 'http://localhost:8081/mine'
```

Check that the chain of old nodes is replaced based on consensus.

```Shell
curl -X GET 'http://localhost:8080/chain'
curl -X GET 'http://localhost:8080/nodes/resolve'
curl -X GET 'http://localhost:8080/chain'
```
