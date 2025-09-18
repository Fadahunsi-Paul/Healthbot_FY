#!/usr/bin/env python3
"""
Comprehensive test script for the AI system with clean dataset
Tests: exact questions, keywords, paraphrasing, and full QA flow
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.getcwd())

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Suppress TensorFlow warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from nlp.service.services import get_answer
import pandas as pd

def test_comprehensive_system():
    """Comprehensive test of the AI system with clean dataset"""
    print("🧪 COMPREHENSIVE AI SYSTEM TEST")
    print("=" * 80)
    print("Testing: Exact Questions | Keywords | Paraphrasing | Full QA Flow")
    print("=" * 80)
    
    # Load sample questions from the clean dataset
    try:
        df = pd.read_csv('api/dataset/train_augmented.csv')
        print(f"📊 Loaded clean dataset: {len(df)} questions")
        
        # Get sample questions by qtype
        sample_questions = {}
        for qtype in df['qtype'].unique():
            qtype_questions = df[df['qtype'] == qtype]['Question'].head(3).tolist()
            sample_questions[qtype] = qtype_questions
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    print(f"📋 Found {len(sample_questions)} question types")
    print()
    
    # Test 1: Exact Questions from Dataset
    print("🔍 TEST 1: EXACT QUESTIONS FROM DATASET")
    print("-" * 50)
    exact_success = 0
    exact_total = 0
    
    for qtype, questions in sample_questions.items():
        print(f"\n📝 Testing {qtype} questions:")
        for i, question in enumerate(questions, 1):
            try:
                answer = get_answer(question)
                if answer and not answer.startswith("I don't have specific information") and not answer.startswith("Sorry, I don't know"):
                    exact_success += 1
                    print(f"  ✅ {i}. {question[:60]}...")
                    print(f"     Answer: {answer[:80]}...")
                else:
                    print(f"  ❌ {i}. {question[:60]}...")
                    print(f"     Answer: {answer}")
                exact_total += 1
            except Exception as e:
                print(f"  ❌ {i}. {question[:60]}... - ERROR: {e}")
                exact_total += 1
    
    print(f"\n📈 Exact Questions Success Rate: {exact_success}/{exact_total} ({exact_success/exact_total*100:.1f}%)")
    
    # Test 2: Single Keywords
    print("\n\n🔤 TEST 2: SINGLE KEYWORDS")
    print("-" * 50)
    keywords = [
        "malaria", "diabetes", "hypertension", "cancer", "fever", "headache", 
        "asthma", "arthritis", "migraine", "pneumonia", "tuberculosis", 
        "schistosomiasis", "kidney disease", "anemia", "leukemia", "infection",
        "cough", "cold", "stomach", "pain", "sickness", "illness", "disease"
    ]
    
    keyword_success = 0
    keyword_total = 0
    
    for i, keyword in enumerate(keywords, 1):
        try:
            answer = get_answer(keyword)
            if answer and not answer.startswith("I don't have specific information") and not answer.startswith("Sorry, I don't know"):
                keyword_success += 1
                print(f"  ✅ {i:2d}. {keyword}")
                print(f"     Answer: {answer[:80]}...")
            else:
                print(f"  ❌ {i:2d}. {keyword}")
                print(f"     Answer: {answer}")
            keyword_total += 1
        except Exception as e:
            print(f"  ❌ {i:2d}. {keyword} - ERROR: {e}")
            keyword_total += 1
    
    print(f"\n📈 Single Keywords Success Rate: {keyword_success}/{keyword_total} ({keyword_success/keyword_total*100:.1f}%)")
    
    # Test 3: Paraphrasing
    print("\n\n🔄 TEST 3: PARAPHRASING")
    print("-" * 50)
    paraphrases = [
        ("What is malaria?", "Tell me about malaria", "Can you explain malaria?", "What do you know about malaria?"),
        ("What causes diabetes?", "Why do people get diabetes?", "How does someone develop diabetes?", "What leads to diabetes?"),
        ("What are the symptoms of fever?", "How do you know if you have a fever?", "What does fever feel like?", "Fever signs and symptoms"),
        ("How to treat headache?", "What's the treatment for headache?", "How can I cure a headache?", "Headache remedies"),
        ("How to prevent cancer?", "What can I do to avoid cancer?", "Cancer prevention tips", "How to reduce cancer risk?")
    ]
    
    paraphrase_success = 0
    paraphrase_total = 0
    
    for i, (original, *paraphrases_list) in enumerate(paraphrases, 1):
        print(f"\n📝 Test {i}: Original: '{original}'")
        for j, paraphrase in enumerate(paraphrases_list, 1):
            try:
                answer = get_answer(paraphrase)
                if answer and not answer.startswith("I don't have specific information") and not answer.startswith("Sorry, I don't know"):
                    paraphrase_success += 1
                    print(f"  ✅ {j}. '{paraphrase}'")
                    print(f"     Answer: {answer[:60]}...")
                else:
                    print(f"  ❌ {j}. '{paraphrase}'")
                    print(f"     Answer: {answer}")
                paraphrase_total += 1
            except Exception as e:
                print(f"  ❌ {j}. '{paraphrase}' - ERROR: {e}")
                paraphrase_total += 1
    
    print(f"\n📈 Paraphrasing Success Rate: {paraphrase_success}/{paraphrase_total} ({paraphrase_success/paraphrase_total*100:.1f}%)")
    
    # Test 4: Follow-up Questions
    print("\n\n💬 TEST 4: FOLLOW-UP QUESTIONS")
    print("-" * 50)
    followup_tests = [
        ("What is malaria?", "What causes it?", "How is it treated?", "How can I prevent it?"),
        ("What is diabetes?", "What are the symptoms?", "How do you manage it?", "What complications can it cause?"),
        ("What is fever?", "What causes fever?", "When should I see a doctor?", "How long does it last?")
    ]
    
    followup_success = 0
    followup_total = 0
    
    for i, (initial, *followups) in enumerate(followup_tests, 1):
        print(f"\n📝 Conversation {i}:")
        history = []
        
        # Initial question
        try:
            answer = get_answer(initial, history=history)
            if answer and not answer.startswith("I don't have specific information") and not answer.startswith("Sorry, I don't know"):
                print(f"  ✅ Initial: '{initial}'")
                print(f"     Answer: {answer[:60]}...")
                history.append({"question": initial, "answer": answer})
                followup_success += 1
            else:
                print(f"  ❌ Initial: '{initial}'")
                print(f"     Answer: {answer}")
            followup_total += 1
        except Exception as e:
            print(f"  ❌ Initial: '{initial}' - ERROR: {e}")
            followup_total += 1
        
        # Follow-up questions
        for j, followup in enumerate(followups, 1):
            try:
                answer = get_answer(followup, history=history)
                if answer and not answer.startswith("I don't have specific information") and not answer.startswith("Sorry, I don't know"):
                    print(f"  ✅ Follow-up {j}: '{followup}'")
                    print(f"     Answer: {answer[:60]}...")
                    history.append({"question": followup, "answer": answer})
                    followup_success += 1
                else:
                    print(f"  ❌ Follow-up {j}: '{followup}'")
                    print(f"     Answer: {answer}")
                followup_total += 1
            except Exception as e:
                print(f"  ❌ Follow-up {j}: '{followup}' - ERROR: {e}")
                followup_total += 1
    
    print(f"\n📈 Follow-up Questions Success Rate: {followup_success}/{followup_total} ({followup_success/followup_total*100:.1f}%)")
    
    # Test 5: Edge Cases
    print("\n\n🎯 TEST 5: EDGE CASES")
    print("-" * 50)
    edge_cases = [
        "hello", "hi", "thanks", "bye",  # Smalltalk
        "xyz123", "random text", "nonsense",  # Nonsense
        "", "   ", "?", "!",  # Empty/special chars
        "what is", "how to", "why",  # Incomplete questions
    ]
    
    edge_success = 0
    edge_total = 0
    
    for i, case in enumerate(edge_cases, 1):
        try:
            answer = get_answer(case)
            # For edge cases, we expect either a smalltalk response or "I don't know"
            if answer and (answer.startswith("I don't have specific information") or 
                          answer.startswith("Sorry, I don't know") or 
                          "hello" in answer.lower() or 
                          "hi" in answer.lower() or
                          "thanks" in answer.lower()):
                edge_success += 1
                print(f"  ✅ {i:2d}. '{case}' -> {answer[:40]}...")
            else:
                print(f"  ❌ {i:2d}. '{case}' -> {answer[:40]}...")
            edge_total += 1
        except Exception as e:
            print(f"  ❌ {i:2d}. '{case}' - ERROR: {e}")
            edge_total += 1
    
    print(f"\n📈 Edge Cases Success Rate: {edge_success}/{edge_total} ({edge_success/edge_total*100:.1f}%)")
    
    # Overall Summary
    print("\n\n🎯 OVERALL SUMMARY")
    print("=" * 80)
    total_success = exact_success + keyword_success + paraphrase_success + followup_success + edge_success
    total_tests = exact_total + keyword_total + paraphrase_total + followup_total + edge_total
    
    print(f"📊 Test Results:")
    print(f"  • Exact Questions:     {exact_success:3d}/{exact_total:3d} ({exact_success/exact_total*100:5.1f}%)")
    print(f"  • Single Keywords:     {keyword_success:3d}/{keyword_total:3d} ({keyword_success/keyword_total*100:5.1f}%)")
    print(f"  • Paraphrasing:        {paraphrase_success:3d}/{paraphrase_total:3d} ({paraphrase_success/paraphrase_total*100:5.1f}%)")
    print(f"  • Follow-up Questions: {followup_success:3d}/{followup_total:3d} ({followup_success/followup_total*100:5.1f}%)")
    print(f"  • Edge Cases:          {edge_success:3d}/{edge_total:3d} ({edge_success/edge_total*100:5.1f}%)")
    print(f"  ────────────────────────────────────────────────────────────────")
    print(f"  • OVERALL:             {total_success:3d}/{total_tests:3d} ({total_success/total_tests*100:5.1f}%)")
    
    # Performance Rating
    overall_rate = total_success/total_tests
    if overall_rate >= 0.9:
        print("\n🎉 EXCELLENT! The system is performing exceptionally well!")
    elif overall_rate >= 0.8:
        print("\n👍 GREAT! The system is performing very well!")
    elif overall_rate >= 0.7:
        print("\n✅ GOOD! The system is performing well!")
    elif overall_rate >= 0.6:
        print("\n⚠️  FAIR! The system needs some improvements.")
    else:
        print("\n❌ POOR! The system needs significant improvements.")
    
    print(f"\n📈 Clean Dataset Performance: {len(df)} questions available")
    print("✅ System successfully switched to train_augmented.csv!")

if __name__ == "__main__":
    test_comprehensive_system()
