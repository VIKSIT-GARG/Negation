# Source map

All listed snapshots are unmodified. Their full licenses are retained.

## Original framework

| Module | Responsibility |
|---|---|
| `dataset.py` | Structured scenes, controlled prompt variants, grouped splitting, validation |
| `metrics.py` | Strict QA, pair metrics, cluster bootstrap, embedding diagnostics |
| `media.py` | Media attachment, hashes and uniform frame extraction |
| `backends.py` | Ollama and installed VLMEvalKit judge adapters |
| `integrations.py` | VLMEvalKit TSV export and official VBench command bridge |
| `report.py` | Escaped standalone HTML reporting |
| `cli.py` / `io.py` | Command orchestration and deterministic serialization |

## Retained upstream source

### VBench

Revision: `fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490` · License: Apache-2.0

| Retained path | Immutable upstream source |
|---|---|

| `third_party/VBench/LICENSE` | [source](https://github.com/Vchitect/VBench/blob/fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490/LICENSE) |

| `third_party/VBench/vbench/__init__.py` | [source](https://github.com/Vchitect/VBench/blob/fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490/vbench/__init__.py) |

| `third_party/VBench/vbench/subject_consistency.py` | [source](https://github.com/Vchitect/VBench/blob/fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490/vbench/subject_consistency.py) |

| `third_party/VBench/vbench/background_consistency.py` | [source](https://github.com/Vchitect/VBench/blob/fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490/vbench/background_consistency.py) |

| `third_party/VBench/vbench/cli/evaluate.py` | [source](https://github.com/Vchitect/VBench/blob/fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490/vbench/cli/evaluate.py) |

### VLMEvalKit

Revision: `dfdf3fc92480878517cd984b1c2a48e6e8c82880` · License: Apache-2.0

| Retained path | Immutable upstream source |
|---|---|

| `third_party/VLMEvalKit/LICENSE` | [source](https://github.com/open-compass/VLMEvalKit/blob/dfdf3fc92480878517cd984b1c2a48e6e8c82880/LICENSE) |

| `third_party/VLMEvalKit/vlmeval/vlm/base.py` | [source](https://github.com/open-compass/VLMEvalKit/blob/dfdf3fc92480878517cd984b1c2a48e6e8c82880/vlmeval/vlm/base.py) |

| `third_party/VLMEvalKit/vlmeval/dataset/image_base.py` | [source](https://github.com/open-compass/VLMEvalKit/blob/dfdf3fc92480878517cd984b1c2a48e6e8c82880/vlmeval/dataset/image_base.py) |

### NegBench

Revision: `2ac009b5adfb18d1d7c185c466b2bced10f43f6a` · License: MIT

| Retained path | Immutable upstream source |
|---|---|

| `third_party/NegBench/LICENSE` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/LICENSE) |

| `third_party/NegBench/synthetic_datasets/evaluation/README.md` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/synthetic_datasets/evaluation/README.md) |

| `third_party/NegBench/synthetic_datasets/evaluation/process_caption_objects.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/synthetic_datasets/evaluation/process_caption_objects.py) |

| `third_party/NegBench/synthetic_datasets/evaluation/filter_negative_objects.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/synthetic_datasets/evaluation/filter_negative_objects.py) |

| `third_party/NegBench/synthetic_datasets/evaluation/create_mcq.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/synthetic_datasets/evaluation/create_mcq.py) |

| `third_party/NegBench/synthetic_datasets/evaluation/paraphrase_captions.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/synthetic_datasets/evaluation/paraphrase_captions.py) |

| `third_party/NegBench/synthetic_datasets/evaluation/process_video_tasks.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/synthetic_datasets/evaluation/process_video_tasks.py) |

| `third_party/NegBench/benchmarks/LICENSE` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/benchmarks/LICENSE) |

| `third_party/NegBench/benchmarks/src/evaluation/mcq.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/benchmarks/src/evaluation/mcq.py) |

| `third_party/NegBench/benchmarks/src/evaluation/retrieval.py` | [source](https://github.com/m1k2zoo/negbench/blob/2ac009b5adfb18d1d7c185c466b2bced10f43f6a/benchmarks/src/evaluation/retrieval.py) |
