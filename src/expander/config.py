from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    embed_model: str = Field(
        default="ibm-granite/granite-embedding-30m-english",
        description="The model to use for embedding text.",
    )
    example_doc_url: str = Field(
        default="https://docs.redhat.com/en/documentation/red_hat_ai_inference_server/3.2/html-single/getting_started/index",
        description="An example document URL to use for testing.",
    )
    example_pdf_url: str = Field(
        default="https://docs.redhat.com/en/documentation/red_hat_ai_inference_server/3.2/pdf/getting_started/Red_Hat_AI_Inference_Server-3.2-Getting_started-en-US.pdf",
        description="An example PDF URL to use for testing.",
    )
    temporary_storage_path: str = Field(
        default="./tmp/",
        description="Path to temporary storage for downloaded documents.",
    )


settings = Settings()
