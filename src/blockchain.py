import hashlib
import json
import os
from time import time
from urllib.parse import urlparse
from uuid import uuid4

from flask import Flask, jsonify, request
import requests

class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []
    self.nodes = set()

    # Generate the genesis block
    self.new_block(previous_hash=1, proof=100)

  def new_block(self, proof, previous_hash=None):
    """
    Generate a new block in the blockchain.
    :param proof: <int> proof obtained from the proof-of-work algorithm
    :param previous_hash: (optional) <str> hash of the previous block
    :return: <dict> new block
    """
    block = {
      'index': len(self.chain) + 1,
      'timestamp': time(),
      'transactions': self.current_transactions,
      'proof': proof,
      'previous_hash': previous_hash or self.hash(self.chain[-1]),
    }
    # Reset current transaction list
    self.current_transactions = []

    self.chain.append(block)
    return block

  def new_transaction(self, sender, recipient, amount):
    """
    Create a new transaction to add to the next block to be mined
    :param sender: <str> sender's address
    :param recipient: <str> recipient's address
    :param amount: <int> amount
    :return: <int> address of the block containing this transaction
    """
    self.current_transactions.append({
      'sender': sender,
      'recipient': recipient,
      'amount': amount,
    })
    return self.last_block['index'] + 1

  @staticmethod
  def hash(block):
    """
    Create a SHA-256 hash of a block
    :param block: <dict> block
    :return: <str> block
    """
    # The dictionary (dictionary type object) must always be sorted. Otherwise, it will be an inconsistent hash.
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

  @property
  def last_block(self):
    return self.chain[-1]

  def proof_of_work(self, last_proof):
    """
    Simple proof-of-work algorithm:
     - find p' such that the first four of hash(pp')
     - Find p' such that the first 4 of hash(pp') are 0
     - p is the proof of the previous block, p' is the proof of the new block
    :param last_proof: <int>
    return: <int>
    """
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
      proof += 1

    return proof

  @staticmethod
  def valid_proof(last_proof, proof):
    """
    Check that the proofs are correct: are the first 4 of hash(last_proof, proof) 0?
    :param last_proof: <int> previous proof
    :param proof: <int> current proof
    return: <bool> true if correct, false otherwise
    """
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:4] == "0000"

  def register_node(self, address):
    """
    Add a new node to the node list
    :param address: <str> address of the node Example: 'http://192.168.0.5:5000'
    :return: None
    """
    parsed_url = urlparse(address)
    self.nodes.add(parsed_url.netloc)

  def valid_chain(self, chain):
    """
    Check if the blockchain is correct
    :param chain: <list> blockchain
    return: <bool> True for correct, False for not
    """
    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
      block = chain[current_index]
      print(f'{last_block}')
      print(f'{block}')
      print("\n--------------\n")

      # Verify that the hash of the block is correct
      if block['previous_hash'] != self.hash(last_block):
        return False

      # Ensure proof-of-work is correct
      if not self.valid_proof(last_block['proof'], block['proof']):
        return False

      last_block = block
      current_index += 1

    return True

  def resolve_conflicts(self):
    """
    The longest chain on the network replaces its own chain to resolve the conflict
    :return: <bool> True if the chain replaces itself, False otherwise
    """
    neighbours = self.nodes
    new_chain = None

    max_length = len(self.chain)

    # Check the chain of all other nodes
    for node in neighbours:
      response = requests.get(f'http://{node}/chain')

      if response.status_code == 200:
        length = response.json()['length']
        chain = response.json()['chain']

        # Check if that chain is longer or valid
        if length > max_length and self.valid_chain(chain):
          max_length = length
          new_chain = chain

    # If it finds a longer and more valid chain than its own, it will replace it.
    if new_chain:
      self.chain = new_chain
      return True

    return False

# Create a node
app = Flask(__name__)

# Create a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate blockchain class
blockchain = Blockchain()

@app.route('/transactions/new', methods=['POST'])
def new_transactions():
  values = request.get_json()

  # validation
  required = ['sender', 'recipient', 'amount']
  if not all(k in values for k in required):
    return 'Missing values', 400

  # Create a new transaction
  index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

  response = {
    'message': f'Transaction has been added to block {index}'
  }
  return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine():
  # Use proof-of-work algorithm to find the next proof
  last_block = blockchain.last_block
  last_proof = last_block['proof']
  proof = blockchain.proof_of_work(last_proof)

  # Get rewarded for finding a proof
  # Sender sets “0” to indicate that the miner has mined new coins
  blockchain.new_transaction(
    sender="0",
    recipient=node_identifier,
    amount=1,
  )

  # Mining new blocks by adding new blocks to the chain
  block = blockchain.new_block(proof)
  response = {
    'message': 'New blocks mined',
    'index': block['index'],
    'transactions': block['transactions'],
    'proof': block['proof'],
    'previous_hash': block['previous_hash'],
  }
  return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
  response = {
    'chain': blockchain.chain,
    'length': len(blockchain.chain),
  }
  return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
  values = request.get_json()

  nodes = values.get('nodes')
  if nodes is None:
    return "Error: List of non-valid nodes", 400

  for node in nodes:
    blockchain.register_node(node)

  response = {
    'message': 'New nodes have been added',
    'total_nodes': list(blockchain.nodes),
  }
  return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
      response = {
        'message': 'Chain has been replaced',
        'new_chain': blockchain.chain
      }
    else:
      response = {
        'message': 'Chain has been verified',
        'chain': blockchain.chain
      }

    return jsonify(response), 200

# Start the server with PORT
if __name__ == '__main__':
  port = os.environ['PORT']
  app.run(host='0.0.0.0', port=port)
