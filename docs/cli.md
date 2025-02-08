# AudioKit CLI Reference

The AudioKit CLI provides tools for managing audio processing pipelines.

## Installation

```bash
pip install audiokit
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