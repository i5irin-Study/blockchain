class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []

  def new_block(self):
    # Generate a new block and add it to the chain.
    pass

  def new_transaction(self):
    # Add a transaction to the list
    pass

  @staticmethod
  def hash(block):
    # Hash the block
    pass

  @property
  def last_block(self):
    pass
