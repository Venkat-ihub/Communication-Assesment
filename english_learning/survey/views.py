
# Create your views here.
# survey/views.py
import requests
from django.shortcuts import render, redirect
from .forms import SurveyForm
from pymongo import MongoClient
import google.generativeai as genai
import json
from django.http import JsonResponse

client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
db = client['profiledb1']  # Database name
collection = db['english_learning']  # Collection name

genai.configure(api_key="")
def survey_view(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thank_you')  # Redirect to a thank you page or another page
    else:
        form = SurveyForm()
    
    return render(request, 'survey/survey.html', {'form': form})


def thank_you_view(request):
    return render(request, 'survey/thank_you.html')



def test_view(request):
    if request.method == 'POST':
        # User's answers from the form
        user_answers = {
            'dropzone1': request.POST.get('dropzone1', ''),  # Drag and drop answer for Parts of Speech
            'tense1': request.POST.get('tense1', ''),        # MCQ answer for Tenses
            'dropzone2': request.POST.get('dropzone2', ''),  # Drag and drop answer for Active/Passive Voice
            'tense2': request.POST.get('tense2', ''),        # MCQ answer for Tenses  
            'verbDropzone': request.POST.get('verbDropzone', ''),
            'vocab1': request.POST.get('vocab1', ''),        # Fill in the blank for Vocabulary
            'vocab2': request.POST.get('vocab2', ''),        # MCQ for Vocabulary
            'vocab3': request.POST.get('vocab3', ''),
            'vocab4': request.POST.get('vocab4', ''),
            'vocab5': request.POST.get('vocab5', ''),
        }

        # Correct answers for evaluation
        correct_answers = {
            'dropzone1': "Adverb",
            'tense1': "a",
            'dropzone2': "The meal is prepared by the chef every day.",
            'tense2': "a",
            'verbDropzone': "runs",
            'vocab1': "a",
            'vocab2': "b",
            'vocab3': "a",
            'vocab4': "b",
            'vocab5': "a"
        }

        # Calculate score
        score = 0
        for key, correct_answer in correct_answers.items():
            if user_answers[key].strip() == correct_answer:
                score += 1

        # Store user answers and score in MongoDB (if needed)
        # collection.insert_one({
        #     'user_answers': user_answers,
        #     'score': score,
        #     'rank': determine_rank(score)
        # })

        # Redirect to results page
        # Calculate grammar and vocabulary scores
        # Calculate scores
        grammar_score = calculate_grammar_score(user_answers, correct_answers)
        vocabulary_score = calculate_vocabulary_score(user_answers, correct_answers)
        # Prepare the evaluation message
        evaluation = generate_ai_evaluation(grammar_score, vocabulary_score)

        # Return the evaluation as JSON
        return JsonResponse({'evaluation': evaluation})
            
        return render(request, 'survey/test_results.html', {
            'score': score,
            'answers': user_answers,
        })

    return render(request, 'survey/test.html')  # Render the test page if not a POST request

def calculate_grammar_score(answers, correct_answers):
    # Implement your logic to calculate grammar score
    score = 0
    # Example logic for scoring
    if answers['dropzone1'].strip().lower() == correct_answers['dropzone1'].lower():
        score += 1
    if answers['tense1'] == correct_answers['tense1']:
        score += 1
    if answers['dropzone2'].strip().lower() == correct_answers['dropzone2'].lower():
        score += 1
    if answers['tense2'] == correct_answers['tense2']:
        score += 1
    if answers['verbDropzone'].strip().lower() == correct_answers['verbDropzone'].lower():
        score += 1
    return score

def calculate_vocabulary_score(answers, correct_answers):
    # Implement your logic to calculate vocabulary score
    score = 0
    # Example logic for scoring
    if answers['vocab1'] == correct_answers['vocab1']:
        score += 1
    if answers['vocab2'] == correct_answers['vocab2']:
        score += 1
    if answers['vocab3'] == correct_answers['vocab3']:
        score += 1
    if answers['vocab4'] == correct_answers['vocab4']:
        score += 1
    if answers['vocab5'] == correct_answers['vocab5']:
        score += 1
    return score

def generate_ai_evaluation(grammar_score, vocabulary_score):
    # Prepare the prompt for the Gemini model
    prompt = f"Evaluate the performance based on the following scores: Grammar Score: {grammar_score}, Vocabulary Score: {vocabulary_score}. Provide feedback and suggestions for improvement."

    # Generate content using the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Assuming the response contains the evaluation
    evaluation_result = response.text  # Get the generated content from the response
    evaluation_message = ""

    # Determine the performance based on scores
    if grammar_score < 3 and vocabulary_score < 3:
        evaluation_message = (
            "This performance is very weak. A score of "
            f"{grammar_score} in Grammar and {vocabulary_score} in Vocabulary indicates significant deficiencies in both areas. "
            "Strengths: It's difficult to identify any strengths based on these scores alone. "
            "The grammar score suggests some basic grammatical understanding, but it's minimal. "
            "Weaknesses: Extremely weak grammatical skills: The low grammar score shows a major lack of understanding of fundamental grammatical rules, "
            "sentence structure, and punctuation. Complete lack of vocabulary: A score of 0 in vocabulary demonstrates a severe inability to use appropriate words "
            "or understand their meanings. This significantly limits communication effectiveness. Overall communication impairment: The combination of weak grammar "
            "and nonexistent vocabulary results in severely compromised communication abilities. It would be very difficult to understand the meaning of any written "
            "work produced with these skill levels. To improve, focused instruction and practice in both grammar and vocabulary are crucial. The learner needs to "
            "start with the absolute basics and gradually build upon their foundation. This may involve using workbooks, flashcards, language learning apps, and "
            "receiving tutoring or instruction from a teacher or tutor."
        )
    elif grammar_score >= 3 and vocabulary_score >= 3:
        evaluation_message = (
            "This performance is satisfactory. A score of "
            f"{grammar_score} in Grammar and {vocabulary_score} in Vocabulary indicates a reasonable understanding of both areas. "
            "Strengths: The scores suggest a good grasp of basic grammatical rules and vocabulary usage. "
            "Weaknesses: However, there is still room for improvement in both areas to achieve a higher level of proficiency. "
            "To enhance skills, continued practice and exposure to more complex grammatical structures and vocabulary are recommended."
        )
    else:
        evaluation_message = (
            "This performance is intermediate. A score of "
            f"{grammar_score} in Grammar and {vocabulary_score} in Vocabulary indicates a mixed understanding of both areas. "
            "Strengths: The scores suggest some understanding of grammatical rules and vocabulary usage. "
            "Weaknesses: However, there are significant areas for improvement. Focused practice on specific grammar rules and vocabulary expansion is recommended."
        )

    return evaluation_message
    return evaluation_result

def determine_rank(score):
    if score >= 90:
        return 'Excellent'
    elif score >= 75:
        return 'Good'
    elif score >= 50:
        return 'Average'
    else:
        return 'Needs Improvement'
