# Contributing to EEH-LLM

Thank you for your interest in contributing to the Ethical Event Horizon (EEH) framework! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/JohnFlyIII/eeh-sim/issues). Before creating a bug report, please check existing issues to avoid duplicates.

**When filing a bug report, please include:**

- **Clear title and description** of the issue
- **Steps to reproduce** the behavior
- **Expected vs. actual behavior**
- **Environment details:**
  - OS (macOS, Linux, Windows)
  - Python version
  - CUDA/GPU information (if applicable)
  - Model used (e.g., Qwen2.5-32B-Instruct)
- **Error messages** and stack traces
- **Configuration files** (YAML scenarios/configs if relevant)
- **Run outputs** (audit logs, results.json if helpful)

### Suggesting Enhancements

Enhancement suggestions are also tracked as GitHub issues.

**When suggesting an enhancement, please include:**

- **Clear title and description** of the proposed feature
- **Use case**: Why is this enhancement valuable?
- **Proposed solution**: How would it work?
- **Alternatives considered**: Other approaches you've thought about
- **Examples**: Mock-ups, code snippets, or scenario descriptions

**Areas particularly open to enhancement:**

- New ethical scenarios beyond no-fault collisions
- Additional evaluation metrics for reasoning depth
- Improved visualization techniques
- Model comparison tools
- Performance optimizations
- Better error handling and validation

## Pull Requests

We welcome pull requests! Here's the process:

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/eeh-sim.git
cd eeh-sim
git remote add upstream https://github.com/JohnFlyIII/eeh-sim.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

Use descriptive branch names:
- `feature/add-medical-ethics-scenario`
- `fix/122-json-parsing-unicode`
- `docs/improve-installation-guide`

### 3. Make Your Changes

- Follow the [coding standards](#coding-standards)
- Write tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run all tests
python tests/test_controller.py
python tests/test_backend.py
python tests/test_config.py

# Or run a full integration test
./scripts/run_v3.sh
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add temporal visualization for policy scenarios

- Implement timeline graph for long-term effects
- Add color coding for uncertainty levels
- Update report_v3.py to include new visualization
- Add tests for temporal grouping logic

Closes #123"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- **Clear title** summarizing the change
- **Description** of what changed and why
- **Reference to issue** (e.g., "Closes #123")
- **Testing performed** (what scenarios you tested)
- **Screenshots** (for UI/visualization changes)

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- CUDA-capable GPU (optional but recommended for testing)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/eeh-sim.git
cd eeh-sim

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install development dependencies
pip install pytest black flake8 mypy

# Optional: Install package in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all test modules
python tests/test_controller.py
python tests/test_backend.py
python tests/test_config.py

# With pytest (if installed)
pytest tests/

# Run specific test
python tests/test_controller.py
```

### Running the Framework

```bash
# Set model (use smaller model for faster dev iteration)
export EEH_HF_MODEL="Qwen/Qwen2.5-7B-Instruct"

# Run main script
./scripts/run_v3.sh

# Or run directly
python run_v3.py \
  --scenario scenarios/no_fault_dual_v3.yaml \
  --human configs/pseudo_human_v2.yaml \
  --asi configs/pseudo_asi_v2.yaml \
  --out runs/test.json \
  --verbose
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters (120 for long strings)
- Use descriptive variable names

### Code Formatting

We recommend using `black` for consistent formatting:

```bash
pip install black
black src/ tests/
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Dict, List, Optional

def compute_metrics(chain: List[Dict[str, str]], mode: str) -> Dict[str, float]:
    """Compute evaluation metrics for causal chain"""
    ...
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings:

```python
def run_agent_v3(scn: Dict, cfg: Dict, agent_name: str) -> Dict:
    """
    Run agent with mode-based prompting

    Args:
        scn: Scenario dict with universes and prompt templates
        cfg: Agent configuration dict
        agent_name: Name of agent (pseudo-human or pseudo-asi)

    Returns:
        Dict containing decision, causal_chain, metrics, etc.

    Raises:
        ValueError: If scenario or config is invalid
    """
    ...
```

### Comments

- Write self-documenting code when possible
- Add comments for complex logic or non-obvious decisions
- Avoid obvious comments (e.g., `# Increment counter` for `i += 1`)

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Test one thing per test function
- Use descriptive test names that explain what is being tested

**Example:**

```python
def test_chain_depth_with_branching_structure():
    """Test that chain depth correctly handles branching causal graphs"""
    chain = [
        {"from": "Root", "to": "Branch1"},
        {"from": "Root", "to": "Branch2"},
        {"from": "Branch1", "to": "Merge"},
        {"from": "Branch2", "to": "Merge"}
    ]
    depth = _compute_chain_depth(chain)
    assert depth == 3  # Root → Branch → Merge
```

### Test Coverage

Aim for good coverage of:
- Core algorithms (chain depth, temporal span, root causes)
- Edge cases (empty inputs, malformed data)
- Error handling (invalid configs, missing files)
- JSON parsing (various formats, markdown wrappers)

## Documentation

### README Updates

If your change affects usage, update the README.md:
- Installation instructions
- Configuration options
- Usage examples
- Environment variables

### Scenario Documentation

New scenarios should include:
- YAML file in `scenarios/` directory
- Documentation in `scenario_overview.md` or separate file
- Example output in `examples/` (optional)

### Code Documentation

Update docstrings when:
- Changing function signatures
- Adding new parameters
- Changing return values
- Modifying behavior

## Project Structure

```
eeh-sim/
├── configs/              # Agent configurations
├── scenarios/            # Ethical scenarios (YAML)
├── src/eeh_llm/         # Main source code
│   ├── backend/         # LLM interface
│   ├── reasoning/       # Controller logic
│   ├── plots_v3.py      # Visualization
│   ├── report_v3.py     # HTML reports
│   └── config.py        # Config loaders
├── tests/               # Test suite
├── scripts/             # Runner scripts
├── examples/            # Reference runs
├── docs/                # Additional documentation
├── run_v3.py           # Main entry point
└── README.md           # Primary documentation
```

## Questions or Need Help?

- **Issues**: Open an issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **Email**: Contact john@example.com for private inquiries

## Attribution

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to EEH-LLM!** Your efforts help advance the understanding of intelligence differentials in ethical reasoning.
