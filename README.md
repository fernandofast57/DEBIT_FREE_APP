
# Gold Investment Platform

A platform for gold investment with noble ranks system and blockchain integration.

## Setup

### Backend
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

### Blockchain
1. Install dependencies:
   ```bash
   cd blockchain
   npm install
   ```

2. Run tests:
   ```bash
   npx hardhat test
   ```

## Development
1. Run local blockchain:
   ```bash
   npx hardhat node
   ```

2. Run Flask development server:
   ```bash
   python main.py
   ```

## Testing
- Run backend tests: `pytest tests/ -v`
- Run smart contract tests: `cd blockchain && npx hardhat test`
