- [] Replace all OpenAI calls, embeddings, etc. with Gemini / GCP text-embedding models
- [] Implement adaptive RAG (must minimize hallucination)
  - [] results from Gemini 1.5 flash
  - [] results from vector store (currently IL statutes)
  - [] results from Google seearch
  - [] implement translation from "average user" to "legal expert" to improve the quality of vector search:
    - [] AI on Trial: Legal Models Hallucinate in 1 out of 6 (or More) Benchmarking Queries: 
  - [] eliminate regex / keyword based IL rules
- [] Update Streamlit interface
  - [] implement "developers mode" that displays model rationale
  - [] eliminate explanations (i.e. easy / medium / hard) from the normal user mode
  - [] integrate attorney recommendations as placeholders in UI
- [] Persist chat history
  - [] idenify hosted GCP solution (i.e. firestore or bigquery)
  - [] persist all user conversations into this storage
- [] Implement pydantic validation for all model outputs
- [] Rebuild indexes using GCP hosted vector store (i.e. Vertex AI Vector Search)
- [] Review current content of vector store
  - [] Reload / reindex IL statues
  - [] Review the need for RAPTOR
- [] Complete statutes crawling for all 50 states
  - [] Vectorize all statutes and store in GCP hosted vector store

- Asks from Jonathan
  - Cloud credits?
  - Who has marketing budgets?

# Tech stack:
- langchain/langgraph
- ci: github actions
- db for chat history etc.: ???
- search db:
- deployment: GCP Cloud Run

What already done?
- Replace all OpenAI
- Ci build process
- inital code refactor
- updated stramlit
  
# Step 1
- reindex data and swith to gemini embeddings
- Complete auto deployment process ⋆✴︎˚｡⋆


# Step 2
Quering:
- Implement adaptive RAG ⋆✴︎˚｡⋆
- Persist chat history
- eliminate regex / keyword based IL rules
- Implement pydantic validation for all model outputs ⋆✴︎˚｡⋆⋆✴︎˚｡⋆⋆✴︎˚｡⋆⋆✴︎˚｡⋆
- results from Google seearch


Indexing:
- Review Rapror and indexing code, clean up it ⋆✴︎˚｡⋆
- Rebuild indexes using GCP hosted vector store (i.e. Vertex AI Vector Search) ⋆✴︎˚｡⋆
- Review current content of vector store 💩(may be irrelevant if we're going to reindex)

# Step 3
- implement translation from "average user" to "legal expert" to improve the quality of vector search 💩
- Complete statutes crawling for all 50 states ⋆✴︎˚｡⋆
- 

# Never:
- Asks from Jonathan 🐂💩🐂
- Update Streamlit interface 🐂💩🐂

