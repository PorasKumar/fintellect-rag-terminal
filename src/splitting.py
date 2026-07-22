from langchain_text_splitters import RecursiveCharacterTextSplitter

class SplitText:
    def __init__(self, documents):
        self.documents = documents
   
    def split_document_texts(self, chunk_size, chunk_overlap):

        try:
            text_splitter  = RecursiveCharacterTextSplitter(
                chunk_size = chunk_size,
                chunk_overlap = chunk_overlap,
                length_function = len,
                separators= ["\n\n", "\n", " ",".", ""]
            )

            split_docs = text_splitter.split_documents(self.documents)
            return split_docs

        except Exception as e:
            print(f"\n\nError in splitting docs: \n{e}")
            raise RuntimeError("Error in Splitting Documents into Chunks")