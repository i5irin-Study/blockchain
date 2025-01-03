import hashlib
import json
import time

class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []

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
    pass

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
