# Semantic Leak Scan Contract

Purpose: prevent generated-option evidence from being explained by semantic labels, natural-language option text, renderer output, RAG text, or LLM output.

Forbidden selector-visible fields:

- semantic labels
- public action names
- action family names
- natural-language descriptions
- generator prompt or rationale
- RAG text
- renderer text
- LLM output
- object/entity names as shortcuts
- hidden state
- oracle transition/effect tables
- evaluator metrics
- expected outputs
- baseline outputs

Required future metrics:

```text
semantic_label_visible_to_selector = false
natural_language_description_visible_to_selector = false
renderer_text_visible_to_selector = false
rag_text_visible_to_selector = false
llm_output_visible_to_selector = false
```

