import json
import logging
import os
from pathlib import Path

from llama_parse import LlamaParse
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.retrievers import BaseRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)

from rag.parsers.invoice.models import InvoiceOutput, VendorContractTerms, PaymentDueReport

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


INVOICE_EXTRACT_PROMPT = """\
You are given invoice data below. \
Please extract out relevant information from the invoice into the defined schema - the schema is defined as a function call.\

{invoice_data}
"""

CONTRACT_EXTRACT_PROMPT = """\
You are given a vendor contract below. \
Please extract out the payment terms from the contract into the defined schema - the schema is defined as a function call.\

{contract_doc}
"""

PAYMENTS_DUE_SYSTEM_PROMPT = """\
You are a helpful financial assistant that takes invoice data and vendor contract terms, \
then produces a structured payments due report according to the provided schema. \
You must return all relevant fields clearly and accurately.
"""

PAYMENTS_DUE_USER_PROMPT = """\
You are given the following information:

1. Extracted Invoice Data
{invoice_output}


Based on the above invoice data and vendor contract terms, create a payments due report according \
to the schema defined in the function call.
"""


class InvoiceOutputEvent(Event):
    invoice_output: InvoiceOutput


class InvoiceContractEvent(Event):
    invoice_output: InvoiceOutput
    vendor_terms: VendorContractTerms | None


class HandleQuestionEvent(Event):
    question: str


class QuestionAnsweredEvent(Event):
    question: str
    answer: str


class CollectedAnswersEvent(Event):
    combined_answers: str


class LogEvent(Event):
    msg: str
    delta: bool = False
    # clear_previous: bool = False


class InvoicePaymentsWorkflow(Workflow):
    """Invoice Payments workflow."""

    def __init__(
        self,
        parser: LlamaParse,
        contract_retriever: BaseRetriever,
        llm: LLM | None = None,
        similarity_top_k: int = 20,
        output_dir: str = "data_out",
        **kwargs,
    ) -> None:
        """Init params."""
        super().__init__(**kwargs)

        self.parser = parser
        self.retriever = contract_retriever

        self.llm = llm or OpenAI(model="gpt-4o-mini")
        self.similarity_top_k = similarity_top_k

        out_path = Path(output_dir) / "workflow_output"
        if not out_path.exists():
            out_path.mkdir(parents=True, exist_ok=True)
            os.chmod(str(out_path), 0o0777)
        self.output_dir = out_path

    @step
    async def parse_invoice(self, ctx: Context, ev: StartEvent) -> InvoiceOutputEvent:
        # load output template file
        invoice_output_path = Path(
            f"{self.output_dir}/invoice_output.json"
        )
        if invoice_output_path.exists():
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Loading invoice from cache"))
            invoice_output_dict = json.load(open(str(invoice_output_path), "r"))
            invoice_output = InvoiceOutput.model_validate(invoice_output_dict)
        else:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Parsing invoice"))
            # parse invoice
            docs = await self.parser.aload_data(ev.invoice_path)
            # extract from invoice
            prompt = ChatPromptTemplate.from_messages([
                ("user", INVOICE_EXTRACT_PROMPT)
            ])
            invoice_output = await self.llm.astructured_predict(
                InvoiceOutput,
                prompt,
                invoice_data="\n".join([d.get_content(metadata_mode="all") for d in docs])
            )
            if not isinstance(invoice_output, InvoiceOutput):
                raise ValueError(f"Invalid extraction from invoice: {invoice_output}")
            # save output template to file
            with open(invoice_output_path, "w") as fp:
                fp.write(invoice_output.model_dump_json())
            # json.dump(invoice_output.model_dump(), open(invoice_output_path, "w"))
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=f">> Invoice data: {invoice_output.dict()}"))

        return InvoiceOutputEvent(invoice_output=invoice_output)

    @step
    async def generate_output(
            self, ctx: Context, ev: InvoiceOutputEvent
    ) -> StopEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Generating Payments Due Report"))
        prompt = ChatPromptTemplate.from_messages([
            ("system", PAYMENTS_DUE_SYSTEM_PROMPT),
            ("user", PAYMENTS_DUE_USER_PROMPT)
        ])
        payments_due = await self.llm.astructured_predict(
            PaymentDueReport,
            prompt,
            invoice_output=str(ev.invoice_output.dict()),
            #vendor_terms=str(ev.vendor_terms.dict())
        )

        return StopEvent(result=payments_due)


if __name__ == "__main__":
    async def run():
        import dotenv
        dotenv.load_dotenv("/Users/yuragogin/Legal_LLM/.env")
        import chromadb
        from llama_index.core import StorageContext
        from llama_index.core import VectorStoreIndex
        chroma_client = chromadb.EphemeralClient()
        chroma_collection = chroma_client.create_collection("quickstart")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(nodes=[], storage_context=storage_context)
        workflow = InvoicePaymentsWorkflow(
            LlamaParse(
                api_key="llx-KE0IpdcKYfAPePG9lLsYNFxqNnrGlI52RNIMCMW9yS3CLp8N"
            ),
            index.as_retriever(),
            timeout=500
        )
        handler = workflow.run(invoice_path="/Users/yuragogin/Downloads/attachments/2585e5f7d125285f_ustyugov a.pdf")
        async for event in handler.stream_events():
            if isinstance(event, LogEvent):
                if event.delta:
                    print(event.msg, end="")
                else:
                    print(event.msg)

        response = await handler
        print(str(response))
    import asyncio
    asyncio.run(run())
