class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []

  def new_block(self):
    # Generate a new block and add it to the chain.
    pass

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
    # Hash the block
    pass

  @property
  def last_block(self):
    pass
