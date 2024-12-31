
export class BlockchainValidator {
  static validateAddress(address) {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  }

  static validateAmount(amount) {
    return amount > 0 && amount <= 1000000;
  }

  static validateTransaction(tx) {
    return {
      isValid: this.validateAddress(tx.address) && this.validateAmount(tx.amount),
      errors: []
    };
  }
}
