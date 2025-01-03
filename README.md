# Blockchain Training

## Initial setup

Execute the following command in the project root.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Mine the block.

```
curl -X GET 'http://localhost:8080/mine'
```

Send transaction.

```
curl -X POST -H "Content-type: application/json" -d '{"sender":"i5irin","recipient":"you","amount":5}' 'http://localhost:8080/transactions/new'
```

Check the chain.

```
curl -XGET 'http://localhost:8080/chain'
```
