from django.shortcuts import render, redirect
from .models import NewsPost, TeamMember
from .forms import ConsultationRequestForm


def landing_page(request):
    if request.method == 'POST':
        form = ConsultationRequestForm(request.POST)
        if form.is_valid():
            form.save()
            # redirect после успешного POST — стандартная практика (Post/Redirect/Get),
            # чтобы обновление страницы не отправляло форму повторно
            return redirect('landing_page')
    else:
        form = ConsultationRequestForm()

    news = NewsPost.objects.filter(is_published=True).order_by('-published_at')[:10]
    team = TeamMember.objects.all()  # уже отсортировано по order через Meta.ordering

    return render(request, 'public_site/landing.html', {
        'form': form,
        'news': news,
        'team': team,
    })
