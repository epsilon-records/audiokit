# AudioKit CLI Reference

The AudioKit CLI provides tools for managing audio processing pipelines.

## Installation

### Basic Installation
```bash
pip install audiokit
```

### Install with Additional Features
```bash
# Install with audio effects
pip install "audiokit[effects]"

# Install with analysis tools
pip install "audiokit[analysis]"

# Install with all features
pip install "audiokit[effects,analysis]"
```

### Development Installation
```bash
# Install development dependencies
pip install "audiokit[dev]"
```

## Commands

### Create Pipeline

Create a new audio processing pipeline from a YAML configuration:

```bash
ak create pipeline.yml
```

### List Nodes

List available audio processing nodes:

```bash
ak list-nodes
```

### Generate Template

Generate a template pipeline configuration:

```bash
ak template pipeline.yml --type basic
ak template pipeline.yml --type filter
```

### Validate Configuration

Validate a pipeline configuration:

```bash
ak validate pipeline.yml
ak validate pipeline.yml --strict
```

## Configuration Format

```yaml
nodes:
  - id: input
    type: AudioInputNode
    params:
      channels: 2
      sample_rate: 44100

  - id: filter
    type: AudioFilterNode
    params:
      cutoff: 1000
      resonance: 0.7

connections:
  - from: input
    to: filter
``` 