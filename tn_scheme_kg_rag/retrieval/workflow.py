from typing import TypedDict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class RAGState(TypedDict):
    question: str
    sanitized_question: str
    retrieved_contexts: List[str]
    graph_context: List[dict]
    answer: str
    citations: List[str]
    is_safe: bool

class AnswerSchema(BaseModel):
    answer: str = Field(..., description="Concise citizen-friendly answer grounded strictly in evidence")
    citations: List[str] = Field(..., description="Official scheme names and sources cited")
    missing_information: Optional[str] = Field(None, description="Details not available")

class RAGPipelineOrchestrator:
    def __init__(self, vector_retriever, graph_manager):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        self.retriever = vector_retriever
        self.graph = graph_manager

    def validate_input_node(self, state: RAGState) -> RAGState:
        q = state["question"].strip()
        if len(q) < 3 or len(q) > 500:
            state["is_safe"] = False
            state["answer"] = "Please enter a valid question between 3 and 500 characters."
        else:
            state["is_safe"] = True
            state["sanitized_question"] = q
        return state

    def retrieve_node(self, state: RAGState) -> RAGState:
        if not state["is_safe"]:
            return state
        docs = self.retriever.invoke(state["sanitized_question"])
        state["retrieved_contexts"] = [d.page_content for d in docs]
        state["graph_context"] = self.graph.query_graph(
            "MATCH (s:Scheme)-[r]->(n) WHERE toLower(s.name) CONTAINS toLower($q) RETURN s.name AS scheme, type(r) AS rel, n.name AS target LIMIT 5",
            {"q": state["sanitized_question"][:10]}
        )
        return state

    def generate_node(self, state: RAGState) -> RAGState:
        if not state["is_safe"]:
            return state

        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an official Tamil Nadu Government Schemes Intelligent Assistant.\n"
             "Rules:\n"
             "1. Answer strictly from retrieved official evidence.\n"
             "2. Never invent eligibility criteria, subsidy amounts, or deadlines.\n"
             "3. If evidence is insufficient, state that official sources do not provide enough information."),
            ("human", "Context:\n{context}\n\nGraph Relations:\n{graph_context}\n\nQuestion: {question}")
        ])

        chain = prompt | self.llm.with_structured_output(AnswerSchema)
        result = chain.invoke({
            "context": "\n".join(state["retrieved_contexts"]),
            "graph_context": str(state["graph_context"]),
            "question": state["sanitized_question"]
        })

        state["answer"] = result.answer
        state["citations"] = result.citations
        return state