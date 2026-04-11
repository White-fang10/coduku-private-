from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os

# Create a router for the RAG-enabled AI Code Mentor
router = APIRouter(prefix="/api/v1/mentor", tags=["mentor"])

class AnalyzeRequest(BaseModel):
    problem_id: str
    language: str
    code: str
    user_question: str | None = None

# Initialize LLM and Vector Store components conditionally
_rag_chain = None

def init_rag_chain():
    global _rag_chain
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY not found. RAG Code Mentor will operate in fallback mode.")
        return

    try:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain.prompts import PromptTemplate
        from langchain_community.vectorstores import Chroma
        from langchain.schema.runnable import RunnablePassthrough
        from langchain.schema.output_parser import StrOutputParser
        from langchain.docstore.document import Document

        # 1. Create LLM
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)
        
        # 2. Setup Vector Store (In-memory for simplicity, or local path)
        embeddings = OpenAIEmbeddings()
        
        # Sample coding standards / rules to act as context (The "Vector Store" data)
        knowledge_base = [
            "In Python, always use 4 spaces for indentation.",
            "Avoid using print statements in competitive programming, always return the answer.",
            "Unbounded while True loops can cause Time Limit Exceeded (TLE) errors.",
            "Using recursive functions without a base case will result in RecursionError or Stack Overflow.",
            "When dealing with large inputs in Python, sys.stdin.read().split() is faster than input().",
            "In C++, using ios_base::sync_with_stdio(false); cin.tie(NULL); speeds up standard IO.",
            "For searching, binary search reduces time complexity from O(N) to O(log N).",
            "For two sum, using a hash map lowers the time complexity from O(N^2) to O(N)."
        ]
        
        docs = [Document(page_content=text) for text in knowledge_base]
        vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        # 3. Create RAG Prompt
        template = """
        You are an elite competitive programming AI Mentor.
        Use the following retrieved context along with your built-in knowledge to provide hints and guidance to the user.
        Do NOT give the direct answer or write the full code. Give conceptual hints to help them fix their issue.
        
        Context: {context}
        
        User's Problem ID: {problem_id}
        User's Language: {language}
        User's Code:
        {code}
        
        User's Question (if any): {question}
        
        Provide a helpful and encouraging mentor response:
        """
        prompt = PromptTemplate.from_template(template)

        # 4. Build Chain
        def format_docs(retrieved_docs):
            return "\n\n".join([d.page_content for d in retrieved_docs])

        _rag_chain = (
            {
                "context": retriever | format_docs, 
                "problem_id": lambda x: x["problem_id"],
                "language": lambda x: x["language"],
                "code": lambda x: x["code"],
                "question": lambda x: x.get("question", "")
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        print("RAG Code Mentor initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize RAG Code Mentor: {e}")
        _rag_chain = None

@router.on_event("startup")
async def startup_event():
    init_rag_chain()

@router.post("/analyze")
async def analyze_code_rag(req: AnalyzeRequest):
    if _rag_chain:
        # Use RAG to generate response
        try:
            response = _rag_chain.invoke({
                "problem_id": req.problem_id,
                "language": req.language,
                "code": req.code,
                "question": req.user_question or "What can I improve?"
            })
            return {"analysis": response, "type": "rag_llm"}
        except Exception as e:
            print(f"RAG Chain error: {e}")
            # Fallback to rule-based
            pass

    # Fallback to simple rule-based mentor (Phase 8 original logic)
    code = req.code.lower()
    hints = []
    
    if req.language in ["python", "python3"]:
        if "print(" in code and "return" not in code:
            hints.append("I noticed you are using `print()`. In competitive coding, you usually need to `return` the final answer.")
        if "pass" in code:
            hints.append("You still have a `pass` statement. Don't forget to replace it with actual logic.")
            
    if "while true" in code:
        hints.append("Be careful! Unbounded `while True` loops often cause a Time Limit Exceeded (TLE) error.")

    if len(hints) == 0:
        hints.append("Your code syntax appears completely solid! If you are failing tests, map out the edge cases on pen and paper (like empty arrays or n=0 constraints).")

    return {"analysis": " ".join(hints), "type": "rule_based_fallback"}
