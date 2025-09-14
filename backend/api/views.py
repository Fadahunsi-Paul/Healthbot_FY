import os
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .model.session import ChatSession
from .model.history import History
from .utils.utils import classify_question
from .utils.utils_followup import build_context
from .qa_lookup import get_answer
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from rest_framework.parsers import MultiPartParser, FormParser
from .utils.utils_followup import build_context   
from .model.dailytip import DailyTip
from .serializer import DailyTipSerializer
from .utils.smalltalk import check_smalltalk
from .model.unanswered import Unanswered

class DailyTipView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        today = datetime.date.today()
        daily_tips = DailyTip.objects.filter(date=today).select_related("tip")[:3]

        if not daily_tips.exists():
            # fallback to most recent 3
            daily_tips = DailyTip.objects.select_related("tip").order_by("-date")[:3]

        serializer = DailyTipSerializer(daily_tips, many=True)
        return Response(serializer.data)



class ChatbotAudioAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        session_id = request.data.get("session_id")
        audio_file = request.FILES.get("audio")

        if not audio_file:
            return Response({"error": "No audio file uploaded"}, status=400)

        # Find or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
        else:
            session = ChatSession.objects.create(user=user, title="New Chat")

        # Save audio file in History if field exists
        saved_history = None
        if hasattr(History, "audio"):
            saved_history = History.objects.create(
                session=session, sender="user", audio=audio_file
            )

        try:
            # Save uploaded file to temp
            ext = audio_file.name.split(".")[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_in:
                for chunk in audio_file.chunks():
                    tmp_in.write(chunk)
                tmp_in_path = tmp_in.name

            # Convert to wav (mono 16kHz)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
                if ext == "opus":
                    audio_segment = AudioSegment.from_file(tmp_in_path, format="ogg")
                else:
                    audio_segment = AudioSegment.from_file(tmp_in_path, format=ext)

                audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                audio_segment.export(tmp_out.name, format="wav")
                tmp_wav_path = tmp_out.name

            # Run transcription
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_wav_path) as source:
                audio_data = recognizer.record(source)

            try:
                transcript = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return Response({"error": "Could not understand audio"}, status=400)
            except sr.RequestError:
                try:
                    import whisper
                except ImportError:
                    return Response(
                        {"error": "STT service unavailable and 'openai-whisper' is not installed"},
                        status=500,
                    )
                model = whisper.load_model("base")
                result = model.transcribe(tmp_wav_path)
                transcript = result["text"]

            # Save transcript to history
            if saved_history:
                saved_history.message = transcript
                saved_history.save()
            else:
                History.objects.create(session=session, sender="user", message=transcript)

            # Build context
            N = 6
            recent_qs = session.messages.order_by("-timestamp")[:N]
            recent = list(reversed(list(recent_qs)))
            history = [{"sender": m.sender, "message": m.message} for m in recent]

            try:
                context_text = build_context(history, transcript, max_messages=N)
            except Exception:
                last_user = next(
                    (m["message"] for m in reversed(history) if m["sender"] == "user"),
                    None,
                )
                context_text = f"{last_user} → {transcript}" if last_user else transcript

            label = classify_question(context_text)
            try:
                answer = get_answer(transcript, label, context=context_text, history=history)
            except TypeError:
                answer = get_answer(transcript, label)

            History.objects.create(session=session, sender="bot", message=answer)

            return Response(
                {
                    "session_id": session.id,
                    "transcript": transcript,
                    "label": label,
                    "answer": answer,
                },
                status=200,
            )

        except Exception as e:
            return Response({"error": f"Audio processing failed: {str(e)}"}, status=500)
        finally:
            if "tmp_in_path" in locals() and os.path.exists(tmp_in_path):
                os.remove(tmp_in_path)
            if "tmp_wav_path" in locals() and os.path.exists(tmp_wav_path):
                os.remove(tmp_wav_path)

class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]   

    def post(self, request):
        user = request.user
        user_question = (request.data.get("question") or "").strip()
        session_id = request.data.get("session_id")

        smalltalk = check_smalltalk(user_question)
        if smalltalk:  
            return Response({"answer": smalltalk}, status=200)

        if not user_question:
            return Response({"error": "No question provided"}, status=400)

        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
        else:
            title = user_question[:50] + ("..." if len(user_question) > 50 else "")
            session = ChatSession.objects.create(user=user, title=title)

        History.objects.create(session=session, sender="user", message=user_question)

        N = 6
        recent_qs = session.messages.order_by("-timestamp")[:N]   
        recent = list(reversed(list(recent_qs)))                
        history = [{"sender": m.sender, "message": m.message, "timestamp": m.timestamp} for m in recent]
        context_text = build_context(history, user_question, max_messages=N)

        label = classify_question(context_text)

        answer = get_answer(user_question, label, context=context_text, history=history)

        if not answer or answer.strip().lower() in ["i don't know", "not sure", "unknown"]:
            Unanswered.objects.create(user=user, question=user_question)
            answer = "I’m not sure yet 🤔, but I’ll learn from this question!"

        History.objects.create(session=session, sender="bot", message=answer)

        return Response({
            "session_id": session.id,
            "user_question": user_question,
            "context_used": context_text,
            "label": label,
            "answer": answer
        })

class ChatSessionListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).values(
            "id", "title", "created_at"
        )
        return Response(list(sessions))

class ChatHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        messages = session.messages.values("sender", "message", "timestamp")
        return Response(list(messages))

class ChatSessionDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.delete()
        return Response({"message": "Session deleted successfully"}, status=204)
