from .utils.embedder import embed_text
from .utils.retriever import FaissRetriever
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

retriever = FaissRetriever()  # Load once at startup

class QueryView(APIView):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Missing query"}, status=status.HTTP_400_BAD_REQUEST)

        query_vector = embed_text(query)
        results = retriever.search(query_vector, top_k=3)

        if not results:
            return Response({"message": "Sorry, I don’t know the answer to that."}, status=status.HTTP_200_OK)

        return Response({
            "query": query,
            "best_answer": results[0]["answer"],
            "alternatives": results
        })
