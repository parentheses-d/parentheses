<p align="center">
  <img src="/par_logo.png" alt="Parentheses" width="720">
</p>

<p align="center">
  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://parentheses.site">
    <img src="https://img.shields.io/badge/Website-parentheses.site-4A90E2?style=flat-square" alt="Website">
  </a>
  <a href="https://x.com/prntsprtc">
    <img src="https://img.shields.io/badge/X-@prntsprtc-000000?style=flat-square&logo=x&logoColor=white" alt="X">
  </a>
  <a href="https://github.com/parentheses-d/parentheses/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  </a>
  <a href="https://solana.com">
    <img src="https://img.shields.io/badge/Solana-Powered-14F195?style=flat-square&logo=solana&logoColor=white" alt="Solana">
  </a>
</p>

> A protocol for collaborative AI learning on Solana blockchain

Parentheses is a framework-agnostic protocol that enables AI models to share and exchange knowledge through a decentralized validation system built on Solana. It provides a secure and efficient infrastructure for collaborative learning across different AI architectures.

## Features

- 🤝 Collaborative Knowledge Exchange
- 🔗 Decentralized Validation
- 📊 Performance-based Rewards
- 🛡️ Secure Knowledge Transfer
- ⚡ High-speed Solana Integration
- 🧠 Adaptive Learning Pathways

## Quick Start

1. Install using pip:
```bash
pip install parentheses
```

2. Set up your environment variables:
```bash
export SOLANA_NETWORK=mainnet-beta
export SOLANA_RPC_URL=your-rpc-url
export SECRET_KEY=your-secret-key
```

3. Run with Docker:
```bash
docker-compose up -d
```

## Architecture

The protocol consists of three main components:

- **Knowledge Exchange**: Manages the sharing and validation of AI knowledge
- **Learning Pathways**: Optimizes knowledge routing and integration
- **Blockchain Integration**: Handles decentralized storage and verification

## API Documentation

Full API documentation is available at [docs.parentheses.site](https://docs.parentheses.site)

### Example

```python
from parentheses import KnowledgeExchange

# Initialize the exchange
exchange = KnowledgeExchange(network="mainnet-beta")

# Submit knowledge
knowledge_data = {
    "content": {"type": "model_weights", "data": ...},
    "domain": "computer_vision",
    "version": "1.0.0"
}
transaction_id = await exchange.submit_knowledge(knowledge_data)
```

## Development

```bash
# Clone the repository
git clone https://github.com/parentheses-d/parentheses.git

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Community

- Website: [parentheses.site](https://parentheses.site)
- Twitter: [@prntsprtc](https://x.com/prntsprtc)

## Security

For security concerns, please email security@parentheses.site

## Acknowledgments

Special thanks to the Solana Foundation and our community contributors.