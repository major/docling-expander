# Testing expanding chunks with Docling

The goal of this script is to take a chunk of text from a docling document and work back to the section header of the document that contains the chunk.
This would allow us to expand the chunk with additional context from the document.

The [main.py](src/expander/main.py) file performs a test with some [Red Hat documentation](https://docs.redhat.com/en/documentation/red_hat_ai_inference_server/3.2/html-single/getting_started/index) to find the parent subchapter of a list item returned as a chunk.

To test this yourself, run:

```bash
git clone https://github.com/major/docling-expander
cd docling-expander
uv run src/expander/main.py
```

> Note: There is an open Docling bug that prevents the code from working correctly with code blocks in list items.
>
> See [docling#2103](https://github.com/docling-project/docling/issues/2103) for more details.
