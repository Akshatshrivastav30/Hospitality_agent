import markdown  # Add this import
from django.shortcuts import render
from .agent_logic import run_hospitality_agent

def index(request):
    result = None
    if request.method == "POST":
        user_query = request.POST.get('query')
        raw_result = run_hospitality_agent(user_query) 
        
        # Convert the Markdown text into HTML
        result = markdown.markdown(raw_result)
        
    return render(request, 'dashboard/index.html', {'result': result})