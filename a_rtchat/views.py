from django.shortcuts import render
from .models import ChatGroup
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ChatmessagesCreateForm

# Create your views here.
@login_required
def chat_view(request):
    chat_groups = get_object_or_404(ChatGroup, group_name='Toofani-chat')
    chat_messages = chat_groups.chat_messages.all()
    form = ChatmessagesCreateForm()

    if request.htmx:
        form = ChatmessagesCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_groups
            message.save()
            context = {
                'chat_message': message,
                'user': request.user,
            }
            return render(request, 'a_rtchat/partials/chat_message_p.html', context)
    return render(request, 'a_rtchat/chat.html', {'chat_messages': chat_messages, 'form': form})
